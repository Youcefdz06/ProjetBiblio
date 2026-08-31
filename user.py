from contextlib import closing
from database import get_connection


# ShowStock
def show_books_stock():
    with closing(get_connection()) as connection:
        books = connection.execute(
            """
            SELECT id, title, description, author, purchase_price, rental_price, stock
            FROM books
            ORDER BY id
            """
        ).fetchall()
    return books


# UserBalance
def get_user_balance(user_id):
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT balance FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    return round(row["balance"], 2)


# BuyBook
def buy_book(id_book, user_id):
    """Purchase one copy of a book for user_id.
    Returns {"title": ..., "balance": ...} or raises ValueError with a
    user-facing message ("Book not found", out of stock, not enough balance)."""
    with closing(get_connection()) as connection, connection:
        book = connection.execute(
            "SELECT id, title, purchase_price, stock FROM books WHERE id = ?",
            (id_book,),
        ).fetchone()
        if book is None:
            raise ValueError("Book not found.")
        if book["stock"] <= 0:
            raise ValueError("The book is out of stock!")

        stock_update = connection.execute(
            "UPDATE books SET stock = stock - 1 WHERE id = ? AND stock > 0",
            (id_book,),
        )
        if stock_update.rowcount != 1:
            raise ValueError("The book is out of stock!")

        # Guard the balance check in the same UPDATE so two purchases can't
        # both pass a stale "enough balance" check at the same time.
        balance_update = connection.execute(
            """
            UPDATE users
            SET balance = ROUND(balance - ?, 2)
            WHERE id = ? AND balance >= ?
            """,
            (book["purchase_price"], user_id, book["purchase_price"]),
        )
        if balance_update.rowcount != 1:
            raise ValueError("Not enough balance!")

        new_balance = connection.execute(
            "SELECT balance FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()["balance"]

        connection.execute(
            """
            INSERT INTO purchases (user_id, book_id, quantity, unit_price)
            VALUES (?, ?, 1, ?)
            """,
            (user_id, id_book, book["purchase_price"]),
        )

    return {"title": book["title"], "balance": new_balance}


# RentBook
def rent_book(id_book, user_id):
    """Rent one copy of a book for user_id.
    Returns {"title", "balance", "rental_id", "due_at"} or raises ValueError."""
    with closing(get_connection()) as connection, connection:
        book = connection.execute(
            "SELECT id, title, rental_price, stock FROM books WHERE id = ?",
            (id_book,),
        ).fetchone()
        if book is None:
            raise ValueError("Book not found.")
        if book["stock"] <= 0:
            raise ValueError("The book is out of stock!")

        stock_update = connection.execute(
            "UPDATE books SET stock = stock - 1 WHERE id = ? AND stock > 0",
            (id_book,),
        )
        if stock_update.rowcount != 1:
            raise ValueError("The book is out of stock!")

        balance_update = connection.execute(
            """
            UPDATE users
            SET balance = ROUND(balance - ?, 2)
            WHERE id = ? AND balance >= ?
            """,
            (book["rental_price"], user_id, book["rental_price"]),
        )
        if balance_update.rowcount != 1:
            raise ValueError("Not enough balance!")

        new_balance = connection.execute(
            "SELECT balance FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()["balance"]

        cursor = connection.execute(
            """
            INSERT INTO rentals (user_id, book_id, quantity, unit_price, status)
            VALUES (?, ?, 1, ?, 'active')
            """,
            (user_id, id_book, book["rental_price"]),
        )
        rental_id = cursor.lastrowid
        due_at = connection.execute(
            "SELECT due_at FROM rentals WHERE id = ?",
            (rental_id,),
        ).fetchone()["due_at"]

    return {
        "title": book["title"],
        "balance": new_balance,
        "rental_id": rental_id,
        "due_at": due_at,
    }


# ReturnBook
def return_book(rental_id, user_id):
    """Return an active rental owned by user_id.
    Returns {"title": ...} or raises ValueError if no matching active rental."""
    with closing(get_connection()) as connection, connection:
        rental = connection.execute(
            """
            SELECT r.id, r.book_id, r.quantity, b.title
            FROM rentals AS r
            JOIN books AS b ON b.id = r.book_id
            WHERE r.id = ? AND r.user_id = ? AND r.status = 'active'
            """,
            (rental_id, user_id),
        ).fetchone()

        if rental is None:
            raise ValueError("Active rental not found.")

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

    return {"title": rental["title"]}


# ShowActiveRentals
def show_rented_books(user_id):
    with closing(get_connection()) as connection:
        rentals = connection.execute(
            """
            SELECT
                r.id AS rental_id,
                r.book_id,
                b.title,
                b.author,
                r.quantity,
                r.unit_price,
                r.rented_at,
                r.due_at
            FROM rentals AS r
            JOIN books AS b ON b.id = r.book_id
            WHERE r.user_id = ? AND r.status = 'active'
            ORDER BY r.due_at, r.id
            """,
            (user_id,),
        ).fetchall()
    return rentals


# TransactionHistory
def show_transaction_history(user_id):
    with closing(get_connection()) as connection:
        transactions = connection.execute(
            """
            SELECT
                'Purchase' AS transaction_type,
                p.id AS transaction_id,
                p.book_id,
                b.title,
                p.unit_price AS price,
                p.purchased_at AS transaction_at
            FROM purchases AS p
            JOIN books AS b ON b.id = p.book_id
            WHERE p.user_id = ?

            UNION ALL

            SELECT
                'Rental' AS transaction_type,
                r.id AS transaction_id,
                r.book_id,
                b.title,
                r.unit_price AS price,
                r.rented_at AS transaction_at
            FROM rentals AS r
            JOIN books AS b ON b.id = r.book_id
            WHERE r.user_id = ?

            ORDER BY transaction_at DESC, transaction_id DESC
            """,
            (user_id, user_id),
        ).fetchall()
    return transactions
