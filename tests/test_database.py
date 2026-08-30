import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from database import get_connection, init_database


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        init_database(self.database_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_required_tables_are_created(self):
        with closing(get_connection(self.database_path)) as connection:
            tables = {
                row["name"]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
                )
            }

        self.assertEqual(tables, {"users", "books", "purchases", "rentals"})

    def test_foreign_keys_are_enforced(self):
        with self.assertRaises(sqlite3.IntegrityError):
            with closing(get_connection(self.database_path)) as connection, connection:
                connection.execute(
                    """
                    INSERT INTO purchases (user_id, book_id, quantity, unit_price)
                    VALUES (999, 999, 1, 10)
                    """
                )

    def test_users_store_password_as_text(self):
        with closing(get_connection(self.database_path)) as connection:
            columns = {
                row["name"]: row["type"]
                for row in connection.execute("PRAGMA table_info(users)")
            }

        self.assertEqual(columns["password"], "TEXT")
        self.assertNotIn("password_hash", columns)

    def test_rental_due_date_is_set_to_fourteen_days(self):
        with closing(get_connection(self.database_path)) as connection, connection:
            user_id = connection.execute(
                """
                INSERT INTO users (username, password, role, balance)
                VALUES ('student', 'password', 'student', 100)
                """
            ).lastrowid
            book_id = connection.execute(
                """
                INSERT INTO books (
                    title, author, purchase_price, rental_price, stock
                )
                VALUES ('Test Book', 'Test Author', 20, 5, 1)
                """
            ).lastrowid
            rental_id = connection.execute(
                """
                INSERT INTO rentals (
                    user_id, book_id, quantity, unit_price, rented_at
                )
                VALUES (?, ?, 1, 5, '2026-08-28 10:00:00')
                """,
                (user_id, book_id),
            ).lastrowid

            rental = connection.execute(
                "SELECT rented_at, due_at FROM rentals WHERE id = ?",
                (rental_id,),
            ).fetchone()

        self.assertEqual(rental["rented_at"], "2026-08-28 10:00:00")
        self.assertEqual(rental["due_at"], "2026-09-11 10:00:00")


if __name__ == "__main__":
    unittest.main()
