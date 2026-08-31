import hashlib
import hmac
import secrets
from contextlib import closing

from database import get_connection


PASSWORD_ITERATIONS = 310_000


def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt}${digest}"


def verify_password(password, stored_password):
    if not stored_password.startswith("pbkdf2_sha256$"):
        return hmac.compare_digest(password, stored_password)

    try:
        _, iterations, salt, expected = stored_password.split("$", 3)
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            int(iterations),
        ).hex()
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(actual, expected)


def login(username, password):
    """Look up a user by username and verify their password.

    If the stored password is still legacy plain-text and the password
    matches, it is upgraded to a pbkdf2 hash in the same call.
    Returns the user record, or None if the login is invalid.
    """
    with closing(get_connection()) as connection, connection:
        row = connection.execute(
            """
            SELECT id, username, password, role, balance
            FROM users
            WHERE username = ?
            """,
            (username.strip(),),
        ).fetchone()

        if row is None or not verify_password(password, row["password"]):
            return None

        if not row["password"].startswith("pbkdf2_sha256$"):
            connection.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (hash_password(password), row["id"]),
            )

        return {
            "id": row["id"],
            "username": row["username"],
            "role": row["role"],
            "balance": row["balance"],
        }


def create_account(username, password, role="student"):
    """Create a new account with a securely hashed password.

    Raises ValueError if the username is already taken. `role` is not
    meant to come from the public signup form — the API always passes
    "student" there, so self-signup can never create an admin account.
    """
    username = username.strip()
    with closing(get_connection()) as connection, connection:
        existing = connection.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if existing is not None:
            raise ValueError("That username is already taken.")

        cursor = connection.execute(
            """
            INSERT INTO users (username, password, role, balance)
            VALUES (?, ?, ?, 0)
            """,
            (username, hash_password(password), role),
        )
        user_id = cursor.lastrowid

    return {"id": user_id, "username": username, "role": role, "balance": 0}
