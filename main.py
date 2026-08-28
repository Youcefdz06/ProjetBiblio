from auth import login
from database import init_database
from admin import Book, add_book, read_book
from utilities import ask_yn

current_user = None

print("Welcome to our library!")
print("")

while current_user is None:

    login_username = input("Enter your username:")
    login_password = input("Enter your password:")

    current_user = login(login_username, login_password)

    if current_user is None:
        print("Invalid username or password. Please try again.")


    elif current_user["role"] == "admin":
        print(f"Welcome, {current_user['username']}! You are logged in as an admin.")

        admin_choice = int(input("1-Add books ,2-Modify books list ,3-stats"))

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
                      add_book( B )
                      resume = ask_yn("Do u wanna add another book y/n :")
                      if resume == "n":
                          break
            case 2:
                print("future feature")  
            case 3:
                print("future feature")    

    else:
        print(f"Welcome, {current_user['username']}! You are logged in as a student.")