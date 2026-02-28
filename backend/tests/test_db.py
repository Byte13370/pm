import os
import sqlite3

from app.db import get_board_for_username, initialize_database, replace_board_for_username


def test_initialize_database_creates_schema_and_seed_data(tmp_path) -> None:
    db_path = tmp_path / "pm.db"
    os.environ["PM_DB_PATH"] = str(db_path)

    initialize_database()

    assert db_path.exists()

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    user_count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    board_count = cursor.execute("SELECT COUNT(*) FROM boards").fetchone()[0]
    assert user_count >= 1
    assert board_count >= 1


def test_board_read_and_replace_roundtrip(tmp_path) -> None:
    db_path = tmp_path / "pm.db"
    os.environ["PM_DB_PATH"] = str(db_path)

    initialize_database()

    board = get_board_for_username("user")
    assert "columns" in board
    assert "cards" in board

    board["columns"][0]["title"] = "Renamed"
    updated = replace_board_for_username("user", board)
    assert updated["columns"][0]["title"] == "Renamed"

    reloaded = get_board_for_username("user")
    assert reloaded["columns"][0]["title"] == "Renamed"
