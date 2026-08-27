import sqlite3
from contextlib import closing
from pathlib import Path


DATABASE_PATH = Path(__file__).with_name("library.db")


def get_connection(database_path=DATABASE_PATH):
    """Open a SQLite connection configured for this application."""
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database(database_path=DATABASE_PATH):
    """Create the library database and its tables if they do not exist."""
    with closing(get_connection(database_path)) as connection, connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'student'
                    CHECK (role IN ('admin', 'student')),
                balance REAL NOT NULL DEFAULT 0
                    CHECK (balance >= 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                author TEXT NOT NULL,
                purchase_price REAL NOT NULL
                    CHECK (purchase_price >= 0),
                rental_price REAL NOT NULL
                    CHECK (rental_price >= 0),
                stock INTEGER NOT NULL DEFAULT 0
                    CHECK (stock >= 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (title, author)
            );

            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1
                    CHECK (quantity > 0),
                unit_price REAL NOT NULL
                    CHECK (unit_price >= 0),
                purchased_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON UPDATE CASCADE ON DELETE RESTRICT,
                FOREIGN KEY (book_id) REFERENCES books(id)
                    ON UPDATE CASCADE ON DELETE RESTRICT
            );

            CREATE TABLE IF NOT EXISTS rentals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1
                    CHECK (quantity > 0),
                unit_price REAL NOT NULL
                    CHECK (unit_price >= 0),
                rented_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                due_at TEXT,
                returned_at TEXT,
                status TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'returned')),
                CHECK (
                    (status = 'active' AND returned_at IS NULL)
                    OR (status = 'returned' AND returned_at IS NOT NULL)
                ),
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON UPDATE CASCADE ON DELETE RESTRICT,
                FOREIGN KEY (book_id) REFERENCES books(id)
                    ON UPDATE CASCADE ON DELETE RESTRICT
            );

            CREATE INDEX IF NOT EXISTS idx_books_title
                ON books(title);
            CREATE INDEX IF NOT EXISTS idx_books_author
                ON books(author);
            CREATE INDEX IF NOT EXISTS idx_purchases_user
                ON purchases(user_id);
            CREATE INDEX IF NOT EXISTS idx_purchases_book
                ON purchases(book_id);
            CREATE INDEX IF NOT EXISTS idx_rentals_user_status
                ON rentals(user_id, status);
            CREATE INDEX IF NOT EXISTS idx_rentals_book_status
                ON rentals(book_id, status);
            """
        )

        user_columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(users)")
        }
        if "password_hash" in user_columns and "password" not in user_columns:
            connection.execute(
                "ALTER TABLE users RENAME COLUMN password_hash TO password"
            )


if __name__ == "__main__":
    init_database()
    print(f"Database initialized: {DATABASE_PATH}")
