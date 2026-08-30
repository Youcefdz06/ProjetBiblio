import os

import requests


DEFAULT_API_URL = "https://projetbiblio.onrender.com"


class APIError(Exception):
    pass


class LibraryAPIClient:
    def __init__(self, base_url=None, timeout=90):
        self.base_url = (
            base_url
            or os.getenv("PROJETBIBLIO_API_URL")
            or DEFAULT_API_URL
        ).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _request(self, method, path, **kwargs):
        try:
            response = self.session.request(
                method,
                f"{self.base_url}{path}",
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as error:
            raise APIError(
                "The library server is unavailable. Check your internet connection."
            ) from error

        if response.status_code >= 400:
            try:
                message = response.json().get("detail", "Request failed.")
            except ValueError:
                message = "Request failed."
            raise APIError(message)

        if response.status_code == 204:
            return None
        return response.json()

    def health(self):
        return self._request("GET", "/health")

    def login(self, username, password):
        result = self._request(
            "POST",
            "/auth/login",
            json={"username": username, "password": password},
        )
        self.session.headers["Authorization"] = f"Bearer {result['token']}"
        return result["user"]

    def logout(self):
        try:
            return self._request("POST", "/auth/logout")
        finally:
            self.session.headers.pop("Authorization", None)

    def books(self):
        return self._request("GET", "/books")

    def balance(self):
        return self._request("GET", "/me/balance")["balance"]

    def buy_book(self, book_id):
        return self._request("POST", f"/books/{book_id}/purchase")

    def rent_book(self, book_id):
        return self._request("POST", f"/books/{book_id}/rent")

    def rentals(self):
        return self._request("GET", "/me/rentals")

    def return_rental(self, rental_id):
        return self._request("POST", f"/rentals/{rental_id}/return")

    def transactions(self):
        return self._request("GET", "/me/transactions")

    def add_book(self, book):
        return self._request("POST", "/admin/books", json=book)

    def update_book(self, book_id, book):
        return self._request("PUT", f"/admin/books/{book_id}", json=book)

    def stats(self):
        return self._request("GET", "/admin/stats")
