from contextlib import closing

from database import get_connection


def login(username, password):
    with closing(get_connection()) as connection:
        user = connection.execute(
            """
            SELECT id, username, role, balance
            FROM users
            WHERE username = ? AND password = ?
            """,
            (username.strip(), password),
        ).fetchone()

    if user is None:
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "balance": user["balance"],
    }