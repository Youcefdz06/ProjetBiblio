from dataclasses import dataclass
from contextlib import closing
import sqlite3
from database import get_connection

@dataclass
class Book:
    title:str
    description:str
    author:str 
    purchase_price:float
    rental_price:float
    stock:int

def ask_yn(prompt):
    x = input(prompt).lower()
    while x not in ("y", "n"):
        x = input("please enter y or n : ").lower()
    return x

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

def add_book (Book) :
    with closing(get_connection()) as conn:
        conn.execute(
            """INSERT INTO books (title, description, author, purchase_price, rental_price, stock) VALUES (?, ?, ?, ?, ?, ?)""",
            (Book.title, Book.description, Book.author, Book.purchase_price, Book.rental_price, Book.stock)
        )
        conn.commit()

def modify_books(id_book):
    with closing(get_connection()) as connection, connection:
        book = connection.execute(
            "SELECT * FROM books WHERE id = ?",
            (id_book,),
        ).fetchone()

        if book is None:
            print("Book not found.")
            return

        title = input(f"Title [{book['title']}]: ") or book["title"]
        description = input(f"Description [{book['description']}]: ") or book["description"]
        author = input(f"Author [{book['author']}]: ") or book["author"]
        purchase_price = float(input(f"Purchase price [{book['purchase_price']}]: ") or book["purchase_price"])
        rental_price = float(input(f"Rental price [{book['rental_price']}]: ") or book["rental_price"])
        stock = int( input(f"Stock [{book['stock']}]: ") or book["stock"])

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

        print("Book updated successfully.")
