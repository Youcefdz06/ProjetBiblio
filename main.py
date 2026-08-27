from auth import login
from database import init_database

print("Welcome to our library!")
print("")

current_user = None

while current_user is None:

    login_username = input("Enter your username:")
    login_password = input("Enter your password:")

    current_user = login(login_username, login_password)

    if current_user is None:
        print("Invalid username or password. Please try again.")





    elif current_user["role"] == "admin":
        print(f"Welcome, {current_user['username']}! You are logged in as an admin.")

    else:
        print(f"Welcome, {current_user['username']}! You are logged in as a student.")