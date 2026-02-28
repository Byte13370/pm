import os

from fastapi.testclient import TestClient

from app.main import app


def test_ai_chat_without_board_update_returns_current_board(monkeypatch, tmp_path) -> None:
    os.environ["PM_DB_PATH"] = str(tmp_path / "chat-no-update.db")

    def fake_runner(question, board, history):
        assert question
        assert history == []
        return (
            {
                "assistant_response": "No changes needed.",
                "board_update": None,
            },
            "test-model",
        )

    def fake_run_structured_board_assistant(**kwargs):
        result, model = fake_runner(kwargs["question"], kwargs["board"], kwargs["history"])
        from app.schemas import AIStructuredOutput

        return AIStructuredOutput.model_validate(result), model

    monkeypatch.setattr("app.main.run_structured_board_assistant", fake_run_structured_board_assistant)

    with TestClient(app) as client:
        response = client.post(
            "/api/ai/chat",
            json={"question": "status?", "history": []},
            cookies={"pm_auth": "1"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["assistant_response"] == "No changes needed."
    assert payload["board_updated"] is False
    assert "columns" in payload["board"]


def test_ai_chat_with_board_update_persists_changes(monkeypatch, tmp_path) -> None:
    os.environ["PM_DB_PATH"] = str(tmp_path / "chat-update.db")

    def fake_run_structured_board_assistant(**kwargs):
        from app.schemas import AIStructuredOutput

        updated = kwargs["board"].model_dump()
        updated["columns"][0]["title"] = "AI Updated"
        return (
            AIStructuredOutput.model_validate(
                {
                    "assistant_response": "Updated.",
                    "board_update": updated,
                }
            ),
            "test-model",
        )

    monkeypatch.setattr("app.main.run_structured_board_assistant", fake_run_structured_board_assistant)

    with TestClient(app) as client:
        response = client.post(
            "/api/ai/chat",
            json={"question": "rename", "history": []},
            cookies={"pm_auth": "1"},
        )
        assert response.status_code == 200
        assert response.json()["board_updated"] is True

        board_response = client.get("/api/board", cookies={"pm_auth": "1"})

    assert board_response.status_code == 200
    assert board_response.json()["columns"][0]["title"] == "AI Updated"


def test_ai_chat_malformed_model_output_returns_502(monkeypatch, tmp_path) -> None:
    os.environ["PM_DB_PATH"] = str(tmp_path / "chat-error.db")

    def fake_run_structured_board_assistant(**_kwargs):
        raise RuntimeError("Model output did not match schema")

    monkeypatch.setattr("app.main.run_structured_board_assistant", fake_run_structured_board_assistant)

    with TestClient(app) as client:
        response = client.post(
            "/api/ai/chat",
            json={"question": "bad", "history": []},
            cookies={"pm_auth": "1"},
        )

    assert response.status_code == 502
