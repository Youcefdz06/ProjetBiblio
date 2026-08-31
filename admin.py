from dataclasses import dataclass
from contextlib import closing
from database import get_connection

@dataclass
class Book:
    title:str
    description:str
    author:str 
    purchase_price:float
    rental_price:float
    stock:int

def read_book () :
    print("------------------------------------------------")
    title = input("Enter book title : ")
    description = input("Enter book description : ")
    author = input("Enter book author : ")
    while True:
        try:
            purchase_price = float(input("Enter book purchase price : "))
            rental_price = float(input("Enter book rental price : "))
            break
        except ValueError:
            print("Please enter valid numbers for prices.")
    stock = int(input("Enter book stock : "))   
    print("------------------------------------------------")
    return Book(
       title,
       description,
       author,
       purchase_price,
       rental_price,
       stock
     )

def add_book(book):
    """Insert a new book. `book` just needs title/description/author/
    purchase_price/rental_price/stock attributes (a Book, or the API's
    BookCreate payload both work). Returns the new book's id."""
    with closing(get_connection()) as conn, conn:
        cursor = conn.execute(
            """INSERT INTO books (title, description, author, purchase_price, rental_price, stock) VALUES (?, ?, ?, ?, ?, ?)""",
            (
                book.title.strip(),
                book.description.strip(),
                book.author.strip(),
                book.purchase_price,
                book.rental_price,
                book.stock,
            ),
        )
        return cursor.lastrowid

def get_stats():
    """Compute the admin dashboard numbers: inventory, sales/rental
    activity, low/out-of-stock alerts, overdue rentals, revenue, and
    registered students. Returns a plain dict."""
    with closing(get_connection()) as connection:
        row = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM books) AS book_titles,
                (SELECT COALESCE(SUM(stock), 0) FROM books) AS available_stock,
                (SELECT COALESCE(SUM(quantity), 0) FROM purchases) AS units_sold,
                (SELECT COALESCE(SUM(quantity), 0) FROM rentals) AS units_rented,
                (SELECT COUNT(*) FROM rentals WHERE status = 'active') AS active_rentals,
                (SELECT COUNT(*) FROM books WHERE stock <= 2) AS low_stock_titles,
                (SELECT COUNT(*) FROM books WHERE stock = 0) AS out_of_stock_titles,
                (SELECT COUNT(*) FROM rentals
                    WHERE status = 'active' AND due_at < CURRENT_TIMESTAMP) AS overdue_rentals,
                (SELECT COALESCE(SUM(quantity * unit_price), 0) FROM purchases)
                    + (SELECT COALESCE(SUM(quantity * unit_price), 0) FROM rentals)
                    AS total_revenue,
                (SELECT COUNT(*) FROM users WHERE role = 'student') AS total_students
            """
        ).fetchone()
        return dict(zip(row.keys(), tuple(row)))
    """Update an existing book with already-known new values.
    Returns True on success, or None if the book doesn't exist."""
    with closing(get_connection()) as connection, connection:
        book = connection.execute(
            "SELECT * FROM books WHERE id = ?",
            (id_book,),
        ).fetchone()

        if book is None:
            return None

        connection.execute(
            """
            UPDATE books
            SET title = ?,
                description = ?,
                author = ?,
                purchase_price = ?,
                rental_price = ?,
                stock = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                title,
                description,
                author,
                purchase_price,
                rental_price,
                stock,
                id_book,
            ),
        )
        return True
