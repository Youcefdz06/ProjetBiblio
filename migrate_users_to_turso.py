import os
import sqlite3
from contextlib import closing
from pathlib import Path

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).parent
LOCAL_DATABASE_PATH = PROJECT_DIR / "library.db"


def migrate_users():
    load_dotenv(PROJECT_DIR / ".env")

    database_url = os.getenv("TURSO_DATABASE_URL", "").strip()
    auth_token = os.getenv("TURSO_AUTH_TOKEN", "").strip()
    if not database_url or not auth_token:
        raise RuntimeError(
            "Add TURSO_DATABASE_URL and TURSO_AUTH_TOKEN to .env first."
        )

    import turso_serverless

    with closing(sqlite3.connect(LOCAL_DATABASE_PATH)) as local_connection:
        users = local_connection.execute(
            """
            SELECT id, username, password, role, balance, created_at
            FROM users
            ORDER BY id
            """
        ).fetchall()

    from database import init_database

    init_database()

    with closing(
        turso_serverless.connect(database_url, auth_token=auth_token)
    ) as remote_connection, remote_connection:
        remote_connection.executemany(
            """
            INSERT INTO users (
                id, username, password, role, balance, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                password = excluded.password,
                role = excluded.role,
                balance = excluded.balance
            """,
            users,
        )

    print(f"Migrated {len(users)} user(s) to Turso.")


if __name__ == "__main__":
    migrate_users()
