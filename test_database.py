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


if __name__ == "__main__":
    unittest.main()
