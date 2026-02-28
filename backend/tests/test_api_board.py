import os

from fastapi.testclient import TestClient

from app.main import app


def test_get_board_requires_authentication(tmp_path) -> None:
    os.environ["PM_DB_PATH"] = str(tmp_path / "unauth.db")

    with TestClient(app) as client:
        response = client.get("/api/board")

    assert response.status_code == 401


def test_get_board_returns_data_when_authenticated(tmp_path) -> None:
    os.environ["PM_DB_PATH"] = str(tmp_path / "auth.db")

    with TestClient(app) as client:
        response = client.get("/api/board", cookies={"pm_auth": "1"})

    assert response.status_code == 200
    payload = response.json()
    assert "columns" in payload
    assert "cards" in payload


def test_put_board_updates_board_and_persists(tmp_path) -> None:
    os.environ["PM_DB_PATH"] = str(tmp_path / "persist.db")

    with TestClient(app) as client:
        current = client.get("/api/board", cookies={"pm_auth": "1"})
        assert current.status_code == 200
        board = current.json()

        board["columns"][0]["title"] = "Backend Updated"
        update_response = client.put("/api/board", json=board, cookies={"pm_auth": "1"})

        assert update_response.status_code == 200
        assert update_response.json()["columns"][0]["title"] == "Backend Updated"

        fetched_again = client.get("/api/board", cookies={"pm_auth": "1"})
        assert fetched_again.status_code == 200
        assert fetched_again.json()["columns"][0]["title"] == "Backend Updated"


def test_put_board_rejects_invalid_payload(tmp_path) -> None:
    os.environ["PM_DB_PATH"] = str(tmp_path / "invalid.db")

    with TestClient(app) as client:
        response = client.put(
            "/api/board",
            json={"columns": [{"id": "col-1", "title": "A", "cardIds": ["card-1"]}], "cards": {}},
            cookies={"pm_auth": "1"},
        )

    assert response.status_code == 422


def test_database_file_is_auto_created(tmp_path) -> None:
    db_path = tmp_path / "autocreate.db"
    os.environ["PM_DB_PATH"] = str(db_path)

    assert not db_path.exists()

    with TestClient(app) as client:
        response = client.get("/api/board", cookies={"pm_auth": "1"})
        assert response.status_code == 200

    assert db_path.exists()
