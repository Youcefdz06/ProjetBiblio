import sqlite3

from auth import login
from database import (
    DATABASE_ERRORS,
    INTEGRITY_ERRORS,
    OPERATIONAL_ERRORS,
    init_database,
)
from admin import Book, add_book, read_book
from user import (
    buy_book,
    get_user_balance,
    rent_book,
    return_book,
    show_books_stock,
    show_rented_books,
    show_transaction_history,
)
from utilities import ask_yn

init_database()
current_user = None

print("Welcome to our library!")
print("")

while current_user is None:

    try:
        login_username = input("Enter your username:")
        login_password = input("Enter your password:")
    except (EOFError, KeyboardInterrupt):
        print("Input interrupted. Goodbye.")
        break

    try:
        current_user = login(login_username, login_password)
    except OPERATIONAL_ERRORS:
        print("The database could not be accessed. Close it in DB Browser and try again.")
        break
    except DATABASE_ERRORS:
        print("The database is damaged or invalid.")
        break

    if current_user is None:
        print("Invalid username or password. Please try again.")


    elif current_user["role"] == "admin":
        print(f"Welcome, {current_user['username']}! You are logged in as an admin.")

        while True:
            try:
                admin_choice = int(input("1-Add books ,2-Modify books list ,3-stats"))
                break
            except ValueError:
                print("Please enter 1, 2, or 3.")

        match admin_choice:
            case 1:
                while True :
                   B = read_book()
                   print("------------------------------------------------")
                   print("Title is : ", B.title.upper())
                   print("")
                   print("Description : ",B.description)
                   print("Author is : ", B.author)
                   print("Rental price is at :" ,B.rental_price)
                   print("Purchase price is at :" ,B.purchase_price)
                   print("You're adding ",B.stock ,"copies of this book")
                   print("------------------------------------------------")
                   x = ask_yn("Are the info correct y/n :")
                   if x == "y" : 
                      try:
                          add_book(B)
                      except INTEGRITY_ERRORS:
                          print("This book already exists or contains invalid values.")
                          continue
                      except OPERATIONAL_ERRORS:
                          print("The database could not be accessed.")
                          continue
                      except DATABASE_ERRORS:
                          print("The database is damaged or invalid.")
                          continue
                      except (AttributeError, TypeError):
                          print("The book data is invalid.")
                          continue
                      resume = ask_yn("Do u wanna add another book y/n :")
                      if resume == "n":
                          break
            case 2:
                print("future feature")  
            case 3:
                print("future feature")    
            case _:
                print("Please choose 1, 2, or 3.")

    else:
        print(f"Welcome, {current_user['username']}! You are logged in as a student.")

        user_choice =""

        while user_choice != "1" or user_choice != "2" or user_choice != "3" or user_choice != "4" or user_choice != "5" or user_choice != "6" or user_choice != "7":
            print("Enter the right choice!")
            user_choice = str(input(f"1-View stock ,2-Buy a book ,3-Rent a book ,4-Return a book ,5-Show balance ,6-Show active rentals ,7-Show transaction history"))
            if  user_choice == "1" or user_choice == "2" or user_choice == "3" or user_choice == "4" or user_choice == "5" or user_choice == "6" or user_choice == "7":
                match user_choice:
                    case "1":
                        show_books_stock()
                    case "2":
                        show_books_stock()
                        try:
                            id_book = int(input("Enter the book ID: "))
                        except ValueError:
                            print("The book ID must be a number.")
                            continue

                        current_user["balance"]= get_user_balance(current_user["id"])
                        buy_book(
                            id_book,
                            current_user["id"],
                            current_user["balance"],
                        )
                    case "3":
                        show_books_stock()
                        try:
                            id_book = int(input("Enter the book ID: "))
                        except ValueError:
                            print("The book ID must be a number.")
                            continue
                        current_user["balance"]= get_user_balance(current_user["id"])
                        rent_book(id_book, current_user["id"], current_user["balance"],)

                    case "4":
                        return_book(current_user["id"])
                    case "5":
                        print(f"Your balance is ${get_user_balance(current_user['id']):.2f}")
                    case "6":
                        show_rented_books(current_user["id"])
                    case "7":
                        show_transaction_history(current_user["id"])
                break
                
            
        

