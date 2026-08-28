import sqlite3

from admin import add_book, modify_books, read_book
from auth import login
from database import DATABASE_ERRORS, INTEGRITY_ERRORS, OPERATIONAL_ERRORS, init_database
from menus import admin_menu, login_menu, user_menu
from user import buy_book, get_user_balance, rent_book, return_book, show_books_stock, show_rented_books, show_transaction_history
from utilities import ask_yn

init_database()
current_user = None
print("Welcome to our library!\n")

while current_user is None:
    try:
        username, password = login_menu()
    except (EOFError, KeyboardInterrupt):
        print("Input interrupted. Goodbye.")
        break
    try:
        current_user = login(username, password)
    except OPERATIONAL_ERRORS:
        print("The database could not be accessed.")
        break
    except DATABASE_ERRORS:
        print("The database is damaged or invalid.")
        break
    if current_user is None:
        print("Invalid username or password. Please try again.")
        continue

    if current_user["role"] == "admin":
        print(f"Welcome, {current_user['username']}! You are logged in as an admin.")
        while True:
            choice = admin_menu()
            if choice == 1:
                book = read_book()
                print("Title:", book.title, "Description:", book.description)
                print("Author:", book.author, "Purchase:", book.purchase_price)
                print("Rental:", book.rental_price, "Stock:", book.stock)
                if ask_yn("Are the info correct y/n: ") == "y":
                    try:
                        add_book(book)
                        print("Book added successfully.")
                    except INTEGRITY_ERRORS:
                        print("This book already exists or contains invalid values.")
            elif choice == 2:
                show_books_stock()
                try:
                    modify_books(int(input("Enter the book ID: ")))
                except ValueError:
                    print("Please enter a valid book ID.")
            elif choice == 3:
                print("future feature")
            elif choice == 4:
                current_user = None
                break
    else:
        print(f"Welcome, {current_user['username']}! You are logged in as a student.")
        while True:
            choice = user_menu()
            if choice == "1":
                show_books_stock()
            elif choice == "2":
                show_books_stock()
                try:
                    book_id = int(input("Enter the book ID: "))
                except ValueError:
                    print("The book ID must be a number.")
                    continue
                current_user["balance"] = get_user_balance(current_user["id"])
                buy_book(book_id, current_user["id"], current_user["balance"])
            elif choice == "3":
                show_books_stock()
                try:
                    book_id = int(input("Enter the book ID: "))
                except ValueError:
                    print("The book ID must be a number.")
                    continue
                current_user["balance"] = get_user_balance(current_user["id"])
                rent_book(book_id, current_user["id"], current_user["balance"])
            elif choice == "4":
                return_book(current_user["id"])
            elif choice == "5":
                print(f"Your balance is ${get_user_balance(current_user['id']):.2f}")
            elif choice == "6":
                show_rented_books(current_user["id"])
            elif choice == "7":
                show_transaction_history(current_user["id"])
            elif choice == "8":
                current_user = None
                break
                
            
        

