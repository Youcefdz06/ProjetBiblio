import os
import sqlite3
from contextlib import closing
from pathlib import Path

from dotenv import load_dotenv


DATABASE_PATH = Path(__file__).with_name("library.db")
load_dotenv(Path(__file__).with_name(".env"))


def _database_error_types(error_name, sqlite_error):
    try:
        import turso_serverless
    except ImportError:
        return (sqlite_error,)

    return (sqlite_error, getattr(turso_serverless, error_name))


INTEGRITY_ERRORS = _database_error_types("IntegrityError", sqlite3.IntegrityError)
OPERATIONAL_ERRORS = _database_error_types(
    "OperationalError", sqlite3.OperationalError
)
DATABASE_ERRORS = _database_error_types("DatabaseError", sqlite3.DatabaseError)


def get_connection(database_path=None):
    """Open a local SQLite connection or the configured Turso database."""
    database_url = os.getenv("TURSO_DATABASE_URL", "").strip()
    auth_token = os.getenv("TURSO_AUTH_TOKEN", "").strip()

    if database_path is None and (database_url or auth_token):
        if not database_url or not auth_token:
            raise RuntimeError(
                "TURSO_DATABASE_URL and TURSO_AUTH_TOKEN must both be configured."
            )

        try:
            import turso_serverless
        except ImportError as error:
            raise RuntimeError(
                "Install the Turso driver with: pip install turso_serverless"
            ) from error

        connection = turso_serverless.connect(
            database_url,
            auth_token=auth_token,
        )
        connection.row_factory = turso_serverless.Row
    else:
        connection = sqlite3.connect(database_path or DATABASE_PATH)
        connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database(database_path=None):
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

            CREATE TRIGGER IF NOT EXISTS set_rental_due_at
            AFTER INSERT ON rentals
            WHEN NEW.due_at IS NULL
            BEGIN
                UPDATE rentals
                SET due_at = datetime(NEW.rented_at, '+14 days')
                WHERE id = NEW.id;
            END;

            UPDATE rentals
            SET due_at = datetime(rented_at, '+14 days')
            WHERE due_at IS NULL;

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

        for table_name in ("purchases", "rentals"):
            columns = {
                row["name"]
                for row in connection.execute(f"PRAGMA table_info({table_name})")
            }
            if "balance_before" in columns:
                connection.execute(
                    f"ALTER TABLE {table_name} DROP COLUMN balance_before"
                )
            if "balance_after" in columns:
                connection.execute(
                    f"ALTER TABLE {table_name} DROP COLUMN balance_after"
                )


if __name__ == "__main__":
    init_database()
    if os.getenv("TURSO_DATABASE_URL", "").strip():
        print("Turso database initialized.")
    else:
        print(f"Database initialized: {DATABASE_PATH}")
