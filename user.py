from dataclasses import dataclass
from contextlib import closing
from database import get_connection



def ask_yn(prompt):
    x = input(prompt).lower()
    while x not in ("y", "n"):
        x = input("please enter y or n : ").lower()
    return x

# ShowStock

def show_books_stock():
    with closing(get_connection()) as connection:
        books = connection.execute(
            """
            SELECT id, title, author, purchase_price, rental_price, stock
            FROM books
            ORDER BY Id
            """
        ).fetchall()

    if not books:
        print("No books available")
        return

    for book in books:
        print("__"*60)
        print(f"-{book['Id']}")
        print(f"Title: {book['title']}")
        print(f"Author: {book['author']}")
        print(f"Buy price: ${book['purchase_price']:.2f}")
        print(f"Rent price: ${book['rental_price']:.2f}")
        print(f"Stock: {book['stock']}")
        print("__"*60)

# BuyBook
def buy_book(id_book, user_id, user_balance):
    with closing(get_connection()) as connection, connection:
        book = connection.execute(
            """
            SELECT id, title, purchase_price, stock
            FROM books
            WHERE id = ?
            """,
            (id_book,),
        ).fetchone()

        if book is None:
            print("Book not found")
            return user_balance

        if book["stock"] <= 0:
            print("The book is out of stock!")
            return user_balance

        if book["purchase_price"] > user_balance:
            print("Not enough balance!")
            return user_balance

        confirmation = ask_yn(
            f"Do you want to buy {book['title']}? y/n: "
        )
        if confirmation == "n":
            return user_balance

        user_balance -= book["purchase_price"]

        connection.execute(
            """
            UPDATE books
            SET stock = stock - 1
            WHERE id = ?
            """,
            (id_book,),
        )

        connection.execute(
            """
            UPDATE users
            SET balance = ?
            WHERE id = ?
            """,
            (user_balance, user_id),
        )

        connection.execute(
            """
            INSERT INTO purchases (user_id, book_id, quantity, unit_price)
            VALUES (?, ?, 1, ?)
            """,
            (user_id, id_book, book["purchase_price"]),
        )

        print(f"You bought '{book['title']}'.")
        print(f"New balance: ${user_balance:.2f}")

    return user_balance



# UserBalance
def get_user_balance(user_id):
    with closing(get_connection()) as connection:
        user = connection.execute(
            """
            SELECT balance
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    if user is None:
        return None

    return user["balance"]
