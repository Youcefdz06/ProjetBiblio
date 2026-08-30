from api_client import APIError, LibraryAPIClient
from menus import admin_menu, login_menu, user_menu
from utilities import ask_yn


def print_books(books):
    if not books:
        print("No books available.")
        return
    for book in books:
        print("__" * 40)
        print(f"ID: {book['id']}")
        print(f"Title: {book['title']}")
        print(f"Author: {book['author']}")
        print(f"Buy price: ${book['purchase_price']:.2f}")
        print(f"Rent price: ${book['rental_price']:.2f}")
        print(f"Stock: {book['stock']}")
    print("__" * 40)


def read_number(prompt, number_type=float, default=None):
    while True:
        value = input(prompt).strip()
        if not value and default is not None:
            return default
        try:
            return number_type(value)
        except ValueError:
            print("Please enter a valid number.")


def read_book(existing=None):
    existing = existing or {}

    def text_value(label, key):
        default = existing.get(key)
        prompt = f"{label} [{default}]: " if default is not None else f"{label}: "
        value = input(prompt).strip()
        return value if value else default

    return {
        "title": text_value("Title", "title"),
        "description": text_value("Description", "description") or "",
        "author": text_value("Author", "author"),
        "purchase_price": read_number(
            f"Purchase price [{existing.get('purchase_price')}]: "
            if existing
            else "Purchase price: ",
            float,
            existing.get("purchase_price"),
        ),
        "rental_price": read_number(
            f"Rental price [{existing.get('rental_price')}]: "
            if existing
            else "Rental price: ",
            float,
            existing.get("rental_price"),
        ),
        "stock": read_number(
            f"Stock [{existing.get('stock')}]: " if existing else "Stock: ",
            int,
            existing.get("stock"),
        ),
    }


def print_rentals(rentals):
    if not rentals:
        print("You have no active rentals.")
        return
    for rental in rentals:
        print("__" * 40)
        print(f"Rental ID: {rental['rental_id']}")
        print(f"Book: {rental['title']} by {rental['author']}")
        print(f"Price: ${rental['unit_price']:.2f}")
        print(f"Rented at: {rental['rented_at']}")
        print(f"Due at: {rental['due_at']}")
    print("__" * 40)


def admin_session(client):
    while True:
        choice = admin_menu()
        try:
            if choice == 1:
                book = read_book()
                if ask_yn("Add this book? y/n: ") == "y":
                    print(client.add_book(book)["message"])
            elif choice == 2:
                books = client.books()
                print_books(books)
                book_id = read_number("Enter the book ID: ", int)
                existing = next((book for book in books if book["id"] == book_id), None)
                if existing is None:
                    print("Book not found.")
                    continue
                updated = read_book(existing)
                if ask_yn("Save these changes? y/n: ") == "y":
                    print(client.update_book(book_id, updated)["message"])
            elif choice == 3:
                stats = client.stats()
                print(f"Book titles: {stats['book_titles']}")
                print(f"Available stock: {stats['available_stock']}")
                print(f"Units sold: {stats['units_sold']}")
                print(f"Units rented: {stats['units_rented']}")
                print(f"Active rentals: {stats['active_rentals']}")
            elif choice == 4:
                client.logout()
                return
        except APIError as error:
            print(error)


def student_session(client):
    while True:
        choice = user_menu()
        try:
            if choice == "1":
                print_books(client.books())
            elif choice == "2":
                print_books(client.books())
                book_id = read_number("Enter the book ID: ", int)
                if ask_yn("Confirm purchase? y/n: ") == "y":
                    result = client.buy_book(book_id)
                    print(result["message"])
                    print(f"New balance: ${result['balance']:.2f}")
            elif choice == "3":
                print_books(client.books())
                book_id = read_number("Enter the book ID: ", int)
                if ask_yn("Confirm rental? y/n: ") == "y":
                    result = client.rent_book(book_id)
                    print(result["message"])
                    print(f"New balance: ${result['balance']:.2f}")
                    print(f"Due at: {result['due_at']}")
            elif choice == "4":
                rentals = client.rentals()
                print_rentals(rentals)
                if not rentals:
                    continue
                rental_id = read_number("Enter the rental ID to return: ", int)
                if ask_yn("Confirm return? y/n: ") == "y":
                    print(client.return_rental(rental_id)["message"])
            elif choice == "5":
                print(f"Your balance is ${client.balance():.2f}")
            elif choice == "6":
                print_rentals(client.rentals())
            elif choice == "7":
                transactions = client.transactions()
                if not transactions:
                    print("You have no transaction history.")
                for transaction in transactions:
                    print("__" * 40)
                    print(f"Type: {transaction['transaction_type']}")
                    print(f"Book: {transaction['title']}")
                    print(f"Price: ${transaction['price']:.2f}")
                    print(f"Date: {transaction['transaction_at']}")
            elif choice == "8":
                client.logout()
                return
        except APIError as error:
            print(error)


def main():
    client = LibraryAPIClient()

    print("Starting ProjetBiblio...")
    try:
        client.health()
    except APIError as error:
        print(error)
        return

    while True:
        username, password = login_menu()
        try:
            user = client.login(username, password)
        except APIError as error:
            print(error)
            continue

        print(f"Welcome, {user['username']}! You are logged in as {user['role']}.")
        if user["role"] == "admin":
            admin_session(client)
        else:
            student_session(client)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")
