import sqlite3

from auth import login
from database import init_database
from admin import Book, add_book, read_book
from utilities import ask_yn

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
    except sqlite3.OperationalError:
        print("The database could not be accessed. Close it in DB Browser and try again.")
        break
    except sqlite3.DatabaseError:
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
                      except sqlite3.IntegrityError:
                          print("This book already exists or contains invalid values.")
                          continue
                      except sqlite3.OperationalError:
                          print("The database could not be accessed.")
                          continue
                      except sqlite3.DatabaseError:
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