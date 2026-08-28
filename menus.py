def login_menu():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    return username, password


def admin_menu(): 
    while True:
        try:
            admin_choice = int(input("1-Add books, 2-Modify books list, 3-Stats, 4-Logout: "))
            if admin_choice not in (1, 2, 3, 4):
                raise ValueError
            break
        except ValueError:
            print("Please choose 1, 2, 3, or 4.")

    return admin_choice


def user_menu():
    while True:
        user_choice = input(
            "1-View stock, 2-Buy a book, 3-Rent a book, "
            "4-Return a book, 5-Show balance, 6-Show active rentals, "
            "7-Show transaction history, 8-Logout: "
        )
        if user_choice in ("1", "2", "3", "4", "5", "6", "7", "8"):
            return user_choice
        print("Please choose a valid option.")
