import os
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from fastapi.testclient import TestClient

import api
import database


class APITests(unittest.TestCase):
    def setUp(self):
        os.environ.pop("TURSO_DATABASE_URL", None)
        os.environ.pop("TURSO_AUTH_TOKEN", None)
        self.temp_directory = tempfile.TemporaryDirectory()
        database.DATABASE_PATH = Path(self.temp_directory.name) / "api-test.db"
        api.SESSIONS.clear()
        self.client_context = TestClient(api.app)
        self.client = self.client_context.__enter__()

        with closing(database.get_connection()) as connection:
            connection.execute(
                """
                INSERT INTO users (username, password, role, balance)
                VALUES ('admin', 'adminpass', 'admin', 0),
                       ('student', 'studentpass', 'student', 100)
                """
            )
            connection.execute(
                """
                INSERT INTO books
                    (title, description, author, purchase_price, rental_price, stock)
                VALUES ('Test Book', 'Description', 'Author', 20, 5, 3)
                """
            )
            connection.commit()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        self.temp_directory.cleanup()

    def login(self, username, password):
        response = self.client.post(
            "/auth/login",
            json={"username": username, "password": password},
        )
        self.assertEqual(response.status_code, 200)
        return {"Authorization": f"Bearer {response.json()['token']}"}

    def test_login_upgrades_plain_text_password(self):
        self.login("student", "studentpass")
        with closing(database.get_connection()) as connection:
            password = connection.execute(
                "SELECT password FROM users WHERE username = 'student'"
            ).fetchone()["password"]
        self.assertTrue(password.startswith("pbkdf2_sha256$"))

    def test_student_can_purchase_and_rent(self):
        headers = self.login("student", "studentpass")
        purchase = self.client.post("/books/1/purchase", headers=headers)
        self.assertEqual(purchase.status_code, 200)
        self.assertEqual(purchase.json()["balance"], 80)

        rental = self.client.post("/books/1/rent", headers=headers)
        self.assertEqual(rental.status_code, 200)
        self.assertEqual(rental.json()["balance"], 75)
        self.assertIsNotNone(rental.json()["due_at"])

    def test_student_cannot_use_admin_endpoint(self):
        headers = self.login("student", "studentpass")
        response = self.client.get("/admin/stats", headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_admin_stats_includes_new_fields(self):
        headers = self.login("admin", "adminpass")
        response = self.client.get("/admin/stats", headers=headers)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        for key in ("low_stock_titles", "overdue_rentals", "total_revenue"):
            self.assertIn(key, body)

    def test_admin_can_add_book(self):
        headers = self.login("admin", "adminpass")
        response = self.client.post(
            "/admin/books",
            headers=headers,
            json={
                "title": "New Book",
                "description": "New description",
                "author": "New Author",
                "purchase_price": 25,
                "rental_price": 6,
                "stock": 4,
            },
        )
        self.assertEqual(response.status_code, 201)


if __name__ == "__main__":
    unittest.main()
