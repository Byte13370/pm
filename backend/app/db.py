import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row


DEFAULT_BOARD: dict[str, Any] = {
    "columns": [
        {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
        {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
        {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
        {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
        {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]},
    ],
    "cards": {
        "card-1": {
            "id": "card-1",
            "title": "Align roadmap themes",
            "details": "Draft quarterly themes with impact statements and metrics.",
        },
        "card-2": {
            "id": "card-2",
            "title": "Gather customer signals",
            "details": "Review support tags, sales notes, and churn feedback.",
        },
        "card-3": {
            "id": "card-3",
            "title": "Prototype analytics view",
            "details": "Sketch initial dashboard layout and key drill-downs.",
        },
        "card-4": {
            "id": "card-4",
            "title": "Refine status language",
            "details": "Standardize column labels and tone across the board.",
        },
        "card-5": {
            "id": "card-5",
            "title": "Design card layout",
            "details": "Add hierarchy and spacing for scanning dense lists.",
        },
        "card-6": {
            "id": "card-6",
            "title": "QA micro-interactions",
            "details": "Verify hover, focus, and loading states.",
        },
        "card-7": {
            "id": "card-7",
            "title": "Ship marketing page",
            "details": "Final copy approved and asset pack delivered.",
        },
        "card-8": {
            "id": "card-8",
            "title": "Close onboarding sprint",
            "details": "Document release notes and share internally.",
        },
    },
}


def use_postgres() -> bool:
    return bool(os.getenv("SUPABASE_DB_URL"))


def get_db_url() -> str:
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        raise RuntimeError("SUPABASE_DB_URL is not configured")
    return db_url


def get_db_path() -> Path:
    configured_path = os.getenv("PM_DB_PATH")
    if configured_path:
        return Path(configured_path)

    return Path(__file__).resolve().parents[1] / "data" / "pm.db"


def get_sqlite_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def get_postgres_connection():
    with psycopg.connect(get_db_url(), row_factory=dict_row) as connection:
        yield connection


def initialize_database() -> None:
    if use_postgres():
        initialize_postgres_database()
        return

    initialize_sqlite_database()


def initialize_postgres_database() -> None:
    with get_postgres_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              id BIGSERIAL PRIMARY KEY,
              supabase_user_id UUID NOT NULL UNIQUE,
              email TEXT,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS boards (
              id BIGSERIAL PRIMARY KEY,
              user_id BIGINT NOT NULL UNIQUE,
              board_json JSONB NOT NULL,
              version INTEGER NOT NULL DEFAULT 1,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_users_supabase_user_id ON users(supabase_user_id)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_boards_user_id ON boards(user_id)")

        connection.commit()


def initialize_sqlite_database() -> None:
    with get_sqlite_connection() as connection:
        cursor = connection.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL UNIQUE,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS boards (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL UNIQUE,
              board_json TEXT NOT NULL,
              version INTEGER NOT NULL DEFAULT 1,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              updated_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_boards_user_id ON boards(user_id);
            """
        )

        cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", ("user",))
        user_row = cursor.execute(
            "SELECT id FROM users WHERE username = ?",
            ("user",),
        ).fetchone()

        if user_row is None:
            raise RuntimeError("Failed to ensure default user")

        cursor.execute(
            """
            INSERT OR IGNORE INTO boards (user_id, board_json)
            VALUES (?, ?)
            """,
            (user_row["id"], json.dumps(DEFAULT_BOARD)),
        )

        connection.commit()


def _get_or_create_user_id(
    connection: psycopg.Connection,
    *,
    supabase_user_id: str,
    email: str | None,
) -> int:
    row = connection.cursor().execute(
        """
        INSERT INTO users (supabase_user_id, email)
        VALUES (%s::uuid, %s)
        ON CONFLICT (supabase_user_id)
        DO UPDATE
        SET email = COALESCE(EXCLUDED.email, users.email),
            updated_at = NOW()
        RETURNING id
        """,
        (supabase_user_id, email),
    ).fetchone()

    if row is None:
        raise RuntimeError("Failed to resolve authenticated user")

    return int(row["id"])


def _ensure_board_for_user(connection: psycopg.Connection, user_id: int) -> None:
    connection.cursor().execute(
        """
        INSERT INTO boards (user_id, board_json)
        VALUES (%s, %s::jsonb)
        ON CONFLICT (user_id) DO NOTHING
        """,
        (user_id, json.dumps(DEFAULT_BOARD)),
    )


def get_board_for_user(supabase_user_id: str, email: str | None) -> dict[str, Any]:
    if not use_postgres():
        username = (
            "user"
            if supabase_user_id == "00000000-0000-0000-0000-000000000001"
            else supabase_user_id
        )
        return get_board_for_username(username)

    with get_postgres_connection() as connection:
        user_id = _get_or_create_user_id(
            connection,
            supabase_user_id=supabase_user_id,
            email=email,
        )
        _ensure_board_for_user(connection, user_id)

        row = connection.cursor().execute(
            """
            SELECT board_json::text AS board_json
            FROM boards
            WHERE user_id = %s
            """,
            (user_id,),
        ).fetchone()

        if row is None:
            raise KeyError("Board not found for authenticated user")

        connection.commit()
        return json.loads(row["board_json"])


def replace_board_for_user(
    supabase_user_id: str,
    email: str | None,
    board_data: dict[str, Any],
) -> dict[str, Any]:
    if not use_postgres():
        username = (
            "user"
            if supabase_user_id == "00000000-0000-0000-0000-000000000001"
            else supabase_user_id
        )
        return replace_board_for_username(username, board_data)

    with get_postgres_connection() as connection:
        user_id = _get_or_create_user_id(
            connection,
            supabase_user_id=supabase_user_id,
            email=email,
        )

        connection.cursor().execute(
            """
            INSERT INTO boards (user_id, board_json, version)
            VALUES (%s, %s::jsonb, 1)
            ON CONFLICT (user_id)
            DO UPDATE
            SET board_json = EXCLUDED.board_json,
                version = boards.version + 1,
                updated_at = NOW()
            """,
            (user_id, json.dumps(board_data)),
        )

        connection.commit()

    return board_data


def get_board_for_username(username: str) -> dict[str, Any]:
    if use_postgres():
        raise RuntimeError("get_board_for_username is only supported in SQLite mode")

    with get_sqlite_connection() as connection:
        row = connection.cursor().execute(
            """
            SELECT b.board_json
            FROM boards b
            JOIN users u ON u.id = b.user_id
            WHERE u.username = ?
            """,
            (username,),
        ).fetchone()

        if row is None:
            raise KeyError(f"Board not found for username '{username}'")

        return json.loads(row["board_json"])


def replace_board_for_username(username: str, board_data: dict[str, Any]) -> dict[str, Any]:
    if use_postgres():
        raise RuntimeError("replace_board_for_username is only supported in SQLite mode")

    with get_sqlite_connection() as connection:
        cursor = connection.cursor()

        user_row = cursor.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if user_row is None:
            raise KeyError(f"User not found for username '{username}'")

        cursor.execute(
            """
            UPDATE boards
            SET board_json = ?, version = version + 1, updated_at = datetime('now')
            WHERE user_id = ?
            """,
            (json.dumps(board_data), user_row["id"]),
        )

        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO boards (user_id, board_json) VALUES (?, ?)",
                (user_row["id"], json.dumps(board_data)),
            )

        connection.commit()

    return board_data
