import pytest

from app.ai_chat import _extract_json_payload, build_structured_messages, run_structured_board_assistant
from app.db import DEFAULT_BOARD
from app.schemas import BoardData


def test_extract_json_payload_accepts_plain_json() -> None:
    payload = _extract_json_payload('{"assistant_response":"ok","board_update":null}')
    assert payload["assistant_response"] == "ok"


def test_extract_json_payload_rejects_non_json() -> None:
    with pytest.raises(RuntimeError, match="valid JSON|malformed JSON"):
        _extract_json_payload("not-json")


def test_build_structured_messages_includes_board_and_history() -> None:
    board = BoardData.model_validate(DEFAULT_BOARD)
    messages = build_structured_messages(question="move card", board=board, history=[])

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "Current board JSON" in messages[1]["content"]


def test_run_structured_board_assistant_rejects_invalid_schema(monkeypatch) -> None:
    board = BoardData.model_validate(DEFAULT_BOARD)

    def fake_ask(_messages):
        return '{"wrong":"shape"}', "test-model"

    monkeypatch.setattr("app.ai_chat.ask_openrouter_messages", fake_ask)

    with pytest.raises(RuntimeError, match="did not match schema"):
        run_structured_board_assistant(question="test", board=board, history=[])
