import hashlib
import hmac
import os
import secrets
import threading
from contextlib import asynccontextmanager, closing
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from database import get_connection, init_database


PASSWORD_ITERATIONS = 310_000
SESSION_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "12"))
SESSIONS = {}
SESSIONS_LOCK = threading.Lock()


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    author: str = Field(min_length=1, max_length=200)
    purchase_price: float = Field(ge=0)
    rental_price: float = Field(ge=0)
    stock: int = Field(ge=0)


class BookUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    author: str = Field(min_length=1, max_length=200)
    purchase_price: float = Field(ge=0)
    rental_price: float = Field(ge=0)
    stock: int = Field(ge=0)


def _row_to_dict(row):
    return {key: row[key] for key in row.keys()}


def _hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt}${digest}"


def _verify_password(password, stored_password):
    if not stored_password.startswith("pbkdf2_sha256$"):
        return hmac.compare_digest(password, stored_password)

    try:
        _, iterations, salt, expected = stored_password.split("$", 3)
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            int(iterations),
        ).hex()
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(actual, expected)


def _create_session(user):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_TTL_HOURS)
    with SESSIONS_LOCK:
        SESSIONS[token] = {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "expires_at": expires_at,
        }
    return token, expires_at


def get_current_user(authorization: str = Header(default="")):
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    with SESSIONS_LOCK:
        session = SESSIONS.get(token)
        if session and session["expires_at"] <= datetime.now(timezone.utc):
            SESSIONS.pop(token, None)
            session = None

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid.",
        )
    return {**session, "token": token}


def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )
    return user


@asynccontextmanager
async def lifespan(_app):
    init_database()
    yield


app = FastAPI(
    title="ProjetBiblio API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def login(payload: LoginRequest):
    username = payload.username.strip()
    with closing(get_connection()) as connection:
        user = connection.execute(
            """
            SELECT id, username, password, role, balance
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        if user is None or not _verify_password(payload.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password.",
            )

        if not user["password"].startswith("pbkdf2_sha256$"):
            connection.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (_hash_password(payload.password), user["id"]),
            )
            connection.commit()

        token, expires_at = _create_session(user)
        return {
            "token": token,
            "expires_at": expires_at.isoformat(),
            "user": {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
                "balance": round(user["balance"], 2),
            },
        }


@app.post("/auth/logout")
def logout(user=Depends(get_current_user)):
    with SESSIONS_LOCK:
        SESSIONS.pop(user["token"], None)
    return {"message": "Logged out."}


@app.get("/books")
def list_books(_user=Depends(get_current_user)):
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT id, title, description, author,
                   purchase_price, rental_price, stock
            FROM books
            ORDER BY id
            """
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


@app.get("/me/balance")
def get_balance(user=Depends(get_current_user)):
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT balance FROM users WHERE id = ?",
            (user["id"],),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"balance": round(row["balance"], 2)}


@app.post("/books/{book_id}/purchase")
def purchase_book(book_id: int, user=Depends(get_current_user)):
    with closing(get_connection()) as connection:
        try:
            book = connection.execute(
                "SELECT id, title, purchase_price, stock FROM books WHERE id = ?",
                (book_id,),
            ).fetchone()
            if book is None:
                raise HTTPException(status_code=404, detail="Book not found.")
            if book["stock"] <= 0:
                raise HTTPException(status_code=409, detail="Book is out of stock.")

            stock_update = connection.execute(
                "UPDATE books SET stock = stock - 1 WHERE id = ? AND stock > 0",
                (book_id,),
            )
            if stock_update.rowcount != 1:
                raise HTTPException(status_code=409, detail="Book is out of stock.")

            balance_update = connection.execute(
                """
                UPDATE users
                SET balance = ROUND(balance - ?, 2)
                WHERE id = ? AND balance >= ?
                """,
                (book["purchase_price"], user["id"], book["purchase_price"]),
            )
            if balance_update.rowcount != 1:
                raise HTTPException(status_code=409, detail="Not enough balance.")

            new_balance = connection.execute(
                "SELECT balance FROM users WHERE id = ?",
                (user["id"],),
            ).fetchone()["balance"]
            connection.execute(
                """
                INSERT INTO purchases (user_id, book_id, quantity, unit_price)
                VALUES (?, ?, 1, ?)
                """,
                (user["id"], book_id, book["purchase_price"]),
            )
            connection.commit()
        except HTTPException:
            connection.rollback()
            raise
        except Exception:
            connection.rollback()
            raise

    return {
        "message": f"You bought '{book['title']}'.",
        "balance": new_balance,
    }


@app.post("/books/{book_id}/rent")
def rent_book(book_id: int, user=Depends(get_current_user)):
    with closing(get_connection()) as connection:
        try:
            book = connection.execute(
                "SELECT id, title, rental_price, stock FROM books WHERE id = ?",
                (book_id,),
            ).fetchone()
            if book is None:
                raise HTTPException(status_code=404, detail="Book not found.")
            if book["stock"] <= 0:
                raise HTTPException(status_code=409, detail="Book is out of stock.")

            stock_update = connection.execute(
                "UPDATE books SET stock = stock - 1 WHERE id = ? AND stock > 0",
                (book_id,),
            )
            if stock_update.rowcount != 1:
                raise HTTPException(status_code=409, detail="Book is out of stock.")

            balance_update = connection.execute(
                """
                UPDATE users
                SET balance = ROUND(balance - ?, 2)
                WHERE id = ? AND balance >= ?
                """,
                (book["rental_price"], user["id"], book["rental_price"]),
            )
            if balance_update.rowcount != 1:
                raise HTTPException(status_code=409, detail="Not enough balance.")

            new_balance = connection.execute(
                "SELECT balance FROM users WHERE id = ?",
                (user["id"],),
            ).fetchone()["balance"]
            cursor = connection.execute(
                """
                INSERT INTO rentals (user_id, book_id, quantity, unit_price, status)
                VALUES (?, ?, 1, ?, 'active')
                """,
                (user["id"], book_id, book["rental_price"]),
            )
            rental_id = cursor.lastrowid
            connection.commit()
            rental = connection.execute(
                "SELECT due_at FROM rentals WHERE id = ?",
                (rental_id,),
            ).fetchone()
        except HTTPException:
            connection.rollback()
            raise
        except Exception:
            connection.rollback()
            raise

    return {
        "message": f"You rented '{book['title']}'.",
        "balance": new_balance,
        "rental_id": rental_id,
        "due_at": rental["due_at"],
    }


@app.get("/me/rentals")
def active_rentals(user=Depends(get_current_user)):
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT r.id AS rental_id, r.book_id, b.title, b.author,
                   r.quantity, r.unit_price, r.rented_at, r.due_at
            FROM rentals AS r
            JOIN books AS b ON b.id = r.book_id
            WHERE r.user_id = ? AND r.status = 'active'
            ORDER BY r.due_at, r.id
            """,
            (user["id"],),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


@app.post("/rentals/{rental_id}/return")
def return_rental(rental_id: int, user=Depends(get_current_user)):
    with closing(get_connection()) as connection:
        try:
            rental = connection.execute(
                """
                SELECT r.id, r.book_id, r.quantity, b.title
                FROM rentals AS r
                JOIN books AS b ON b.id = r.book_id
                WHERE r.id = ? AND r.user_id = ? AND r.status = 'active'
                """,
                (rental_id, user["id"]),
            ).fetchone()
            if rental is None:
                raise HTTPException(status_code=404, detail="Active rental not found.")

            connection.execute(
                """
                UPDATE rentals
                SET status = 'returned', returned_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (rental_id,),
            )
            connection.execute(
                "UPDATE books SET stock = stock + ? WHERE id = ?",
                (rental["quantity"], rental["book_id"]),
            )
            connection.commit()
        except HTTPException:
            connection.rollback()
            raise
        except Exception:
            connection.rollback()
            raise

    return {"message": f"You returned '{rental['title']}'."}


@app.get("/me/transactions")
def transaction_history(user=Depends(get_current_user)):
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT 'Purchase' AS transaction_type,
                   p.id AS transaction_id, p.book_id, b.title,
                   p.unit_price AS price, p.purchased_at AS transaction_at
            FROM purchases AS p
            JOIN books AS b ON b.id = p.book_id
            WHERE p.user_id = ?
            UNION ALL
            SELECT 'Rental' AS transaction_type,
                   r.id AS transaction_id, r.book_id, b.title,
                   r.unit_price AS price, r.rented_at AS transaction_at
            FROM rentals AS r
            JOIN books AS b ON b.id = r.book_id
            WHERE r.user_id = ?
            ORDER BY transaction_at DESC, transaction_id DESC
            """,
            (user["id"], user["id"]),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


@app.post("/admin/books", status_code=status.HTTP_201_CREATED)
def add_book(payload: BookCreate, _admin=Depends(require_admin)):
    with closing(get_connection()) as connection:
        try:
            cursor = connection.execute(
                """
                INSERT INTO books
                    (title, description, author, purchase_price, rental_price, stock)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.title.strip(),
                    payload.description.strip(),
                    payload.author.strip(),
                    payload.purchase_price,
                    payload.rental_price,
                    payload.stock,
                ),
            )
            connection.commit()
        except Exception as error:
            connection.rollback()
            if "UNIQUE" in str(error).upper():
                raise HTTPException(status_code=409, detail="Book already exists.")
            raise
    return {"id": cursor.lastrowid, "message": "Book added successfully."}


@app.put("/admin/books/{book_id}")
def update_book(book_id: int, payload: BookUpdate, _admin=Depends(require_admin)):
    with closing(get_connection()) as connection:
        existing = connection.execute(
            "SELECT id FROM books WHERE id = ?",
            (book_id,),
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Book not found.")
        try:
            connection.execute(
                """
                UPDATE books
                SET title = ?, description = ?, author = ?,
                    purchase_price = ?, rental_price = ?, stock = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload.title.strip(),
                    payload.description.strip(),
                    payload.author.strip(),
                    payload.purchase_price,
                    payload.rental_price,
                    payload.stock,
                    book_id,
                ),
            )
            connection.commit()
        except Exception as error:
            connection.rollback()
            if "UNIQUE" in str(error).upper():
                raise HTTPException(status_code=409, detail="Book already exists.")
            raise
    return {"message": "Book updated successfully."}


@app.get("/admin/stats")
def admin_stats(_admin=Depends(require_admin)):
    with closing(get_connection()) as connection:
        row = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM books) AS book_titles,
                (SELECT COALESCE(SUM(stock), 0) FROM books) AS available_stock,
                (SELECT COALESCE(SUM(quantity), 0) FROM purchases) AS units_sold,
                (SELECT COALESCE(SUM(quantity), 0) FROM rentals) AS units_rented,
                (SELECT COUNT(*) FROM rentals WHERE status = 'active') AS active_rentals
            """
        ).fetchone()
    return _row_to_dict(row)
