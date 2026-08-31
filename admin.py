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

def modify_books(id_book, title, description, author, purchase_price, rental_price, stock):
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
