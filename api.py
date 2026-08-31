import os
import secrets
import threading
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

import admin
import auth
import user
from database import init_database


SESSION_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "12"))
SESSIONS = {}
SESSIONS_LOCK = threading.Lock()


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=4, max_length=200)


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


def _rows_to_dicts(rows):
    return [_row_to_dict(row) for row in rows]


def _raise_for_value_error(error):
    message = str(error)
    code = (
        status.HTTP_404_NOT_FOUND
        if "not found" in message.lower()
        else status.HTTP_409_CONFLICT
    )
    raise HTTPException(status_code=code, detail=message)


def _create_session(user_record):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_TTL_HOURS)
    with SESSIONS_LOCK:
        SESSIONS[token] = {
            "id": user_record["id"],
            "username": user_record["username"],
            "role": user_record["role"],
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


def require_admin(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )
    return current_user


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
    user_record = auth.login(payload.username, payload.password)
    if user_record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    token, expires_at = _create_session(user_record)
    return {
        "token": token,
        "expires_at": expires_at.isoformat(),
        "user": {
            "id": user_record["id"],
            "username": user_record["username"],
            "role": user_record["role"],
            "balance": round(user_record["balance"], 2),
        },
    }


@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest):
    try:
        # role is hardcoded to "student" here, not read from the request —
        # self-signup should never be able to grant itself admin access.
        user_record = auth.create_account(
            payload.username, payload.password, role="student"
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))

    token, expires_at = _create_session(user_record)
    return {
        "token": token,
        "expires_at": expires_at.isoformat(),
        "user": {
            "id": user_record["id"],
            "username": user_record["username"],
            "role": user_record["role"],
            "balance": round(user_record["balance"], 2),
        },
    }


@app.post("/auth/logout")
def logout(current_user=Depends(get_current_user)):
    with SESSIONS_LOCK:
        SESSIONS.pop(current_user["token"], None)
    return {"message": "Logged out."}


@app.get("/books")
def list_books(_current_user=Depends(get_current_user)):
    return _rows_to_dicts(user.show_books_stock())


@app.get("/me/balance")
def get_balance(current_user=Depends(get_current_user)):
    balance = user.get_user_balance(current_user["id"])
    if balance is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"balance": balance}


@app.post("/books/{book_id}/purchase")
def purchase_book(book_id: int, current_user=Depends(get_current_user)):
    try:
        result = user.buy_book(book_id, current_user["id"])
    except ValueError as error:
        _raise_for_value_error(error)

    return {
        "message": f"You bought '{result['title']}'.",
        "balance": result["balance"],
    }


@app.post("/books/{book_id}/rent")
def rent_book_route(book_id: int, current_user=Depends(get_current_user)):
    try:
        result = user.rent_book(book_id, current_user["id"])
    except ValueError as error:
        _raise_for_value_error(error)

    return {
        "message": f"You rented '{result['title']}'.",
        "balance": result["balance"],
        "rental_id": result["rental_id"],
        "due_at": result["due_at"],
    }


@app.get("/me/rentals")
def active_rentals(current_user=Depends(get_current_user)):
    return _rows_to_dicts(user.show_rented_books(current_user["id"]))


@app.post("/rentals/{rental_id}/return")
def return_rental(rental_id: int, current_user=Depends(get_current_user)):
    try:
        result = user.return_book(rental_id, current_user["id"])
    except ValueError as error:
        _raise_for_value_error(error)

    return {"message": f"You returned '{result['title']}'."}


@app.get("/me/transactions")
def transaction_history(current_user=Depends(get_current_user)):
    return _rows_to_dicts(user.show_transaction_history(current_user["id"]))


@app.post("/admin/books", status_code=status.HTTP_201_CREATED)
def add_book_route(payload: BookCreate, _admin_user=Depends(require_admin)):
    try:
        book_id = admin.add_book(payload)
    except Exception as error:
        if "UNIQUE" in str(error).upper():
            raise HTTPException(status_code=409, detail="Book already exists.")
        raise
    return {"id": book_id, "message": "Book added successfully."}


@app.put("/admin/books/{book_id}")
def update_book_route(
    book_id: int, payload: BookUpdate, _admin_user=Depends(require_admin)
):
    try:
        updated = admin.modify_books(
            book_id,
            payload.title.strip(),
            payload.description.strip(),
            payload.author.strip(),
            payload.purchase_price,
            payload.rental_price,
            payload.stock,
        )
    except Exception as error:
        if "UNIQUE" in str(error).upper():
            raise HTTPException(status_code=409, detail="Book already exists.")
        raise

    if updated is None:
        raise HTTPException(status_code=404, detail="Book not found.")
    return {"message": "Book updated successfully."}


@app.get("/admin/stats")
def admin_stats(_admin_user=Depends(require_admin)):
    return admin.get_stats()
