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
            ORDER BY id
            """
        ).fetchall()

    if not books:
        print("No books available")
        return

    for book in books:
        print("__"*60)
        print(f"-{book['id']}")
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

        print("------------------------------------------------")
        print("Title:", book["title"])
        print("Purchase price:", book["purchase_price"])
        print("Stock:", book["stock"])
        print("------------------------------------------------")

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

    return round(user["balance"], 2)


# RentBook
def rent_book(id_book, user_id, user_balance):
    with closing(get_connection()) as connection, connection:
            book = connection.execute(
                """
                SELECT id, title, rental_price, stock
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
    
            if book["rental_price"] > user_balance:
                print("Not enough balance!")
                return user_balance
    
            confirmation = ask_yn(
                f"Do you want to buy {book['title']}? y/n: "
            )
            if confirmation == "n":
                return user_balance
    
            user_balance -= book["rental_price"]
    
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
    
            cursor = connection.execute(
                """
                INSERT INTO rentals (user_id, book_id, quantity, unit_price, status)
                VALUES (?, ?, 1, ?, 'active')
                """,
                (user_id, id_book, book["rental_price"]),
            )
            rental_id = cursor.lastrowid
    with closing(get_connection()) as connection:
            rental = connection.execute(
            """
            SELECT due_at
            FROM rentals
            WHERE id = ?
            """,
            (rental_id,),
            ).fetchone()  
            due_date = rental["due_at"]  
    
            print(f"You rent '{book['title']}'.")
            print(f"New balance: ${user_balance:.2f}")
            print(f"You should return it at : ${str(due_date)}")
    
    return user_balance

# ReturnBook



def return_book(user_id):
    rentals = show_rented_books(user_id)
    if not rentals:
        return False

    try:
        rental_id = int(input("Enter the rental ID to return: "))
    except ValueError:
        print("The rental ID must be a number.")
        return False

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
            print("Active rental not found.")
            return False

        confirmation = ask_yn(
            f"Do you want to return {rental['title']}? y/n: "
        )
        if confirmation == "n":
            return False

        connection.execute(
            """
            UPDATE rentals
            SET status = 'returned', returned_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (rental_id,),
        )
        connection.execute(
            """
            UPDATE books
            SET stock = stock + ?
            WHERE id = ?
            """,
            (rental["quantity"], rental["book_id"]),
        )

    print(f"You returned '{rental['title']}'.")
    return True


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

    if not rentals:
        print("You have no active rentals.")
        return []

    print("__" * 60)
    print("Your active rentals")

    for rental in rentals:
        print("__" * 60)
        print(f"Rental ID: {rental['rental_id']}")
        print(f"Book ID: {rental['book_id']}")
        print(f"Title: {rental['title']}")
        print(f"Author: {rental['author']}")
        print(f"Quantity: {rental['quantity']}")
        print(f"Rental price: ${rental['unit_price']:.2f}")
        print(f"Rented at: {rental['rented_at']}")
        print(f"Due at: {rental['due_at']}")

    print("__" * 60)
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

    if not transactions:
        print("You have no purchase or rental history.")
        return []

    print("__" * 60)
    print("Purchase and rental history")

    for transaction in transactions:
        print("__" * 60)
        print(f"Type: {transaction['transaction_type']}")
        print(f"Transaction ID: {transaction['transaction_id']}")
        print(f"Book ID: {transaction['book_id']}")
        print(f"Title: {transaction['title']}")
        print(f"Price: ${transaction['price']:.2f}")
        print(f"Date: {transaction['transaction_at']}")

    print("__" * 60)
    return transactions



