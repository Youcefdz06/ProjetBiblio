import os
import sqlite3
from contextlib import closing
from pathlib import Path

from dotenv import load_dotenv


DATABASE_PATH = Path(__file__).with_name("library.db")
load_dotenv(Path(__file__).with_name(".env"))


class DatabaseRow:
    def __init__(self, columns, values):
        self._columns = tuple(columns)
        self._values = tuple(values)
        self._mapping = dict(zip(self._columns, self._values))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return self._mapping[key]

    def keys(self):
        return self._columns

    def __iter__(self):
        return iter(self._values)


class LibsqlCursorAdapter:
    def __init__(self, cursor):
        self._cursor = cursor

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def _convert(self, row):
        if row is None:
            return None
        columns = [item[0] for item in (self._cursor.description or ())]
        return DatabaseRow(columns, row)

    def fetchone(self):
        return self._convert(self._cursor.fetchone())

    def fetchall(self):
        return [self._convert(row) for row in self._cursor.fetchall()]

    def fetchmany(self, size=None):
        rows = self._cursor.fetchmany() if size is None else self._cursor.fetchmany(size)
        return [self._convert(row) for row in rows]

    def __iter__(self):
        return iter(self.fetchall())


class LibsqlConnectionAdapter:
    def __init__(self, connection):
        self._connection = connection

    def execute(self, sql, parameters=()):
        return LibsqlCursorAdapter(self._connection.execute(sql, parameters))

    def executemany(self, sql, parameters):
        return LibsqlCursorAdapter(self._connection.executemany(sql, parameters))

    def executescript(self, script):
        return self._connection.executescript(script)

    def commit(self):
        return self._connection.commit()

    def rollback(self):
        return self._connection.rollback()

    def close(self):
        return self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, error_type, _error, _traceback):
        if error_type is None:
            self.commit()
        else:
            self.rollback()
        return False


def _database_error_types(error_name, sqlite_error):
    try:
        import libsql
    except ImportError:
        return (sqlite_error,)

    remote_error = getattr(libsql, error_name, libsql.Error)
    return tuple({sqlite_error, remote_error})


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
            import libsql
        except ImportError as error:
            raise RuntimeError(
                "Install the Turso driver with: pip install libsql"
            ) from error

        connection = LibsqlConnectionAdapter(
            libsql.connect(
                database=database_url,
                auth_token=auth_token,
            )
        )
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
