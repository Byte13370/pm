import os

import httpx
import pytest
from fastapi.testclient import TestClient

from app.ai import ask_openrouter
from app.main import app


class MockResponse:
    def __init__(self, status_code: int, payload: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self) -> dict:
        return self._payload


def test_ask_openrouter_requires_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        ask_openrouter("2+2")


def test_ask_openrouter_parses_content(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")

    def fake_post(*_args, **_kwargs):
        return MockResponse(
            200,
            {
                "choices": [
                    {
                        "message": {
                            "content": "4",
                        }
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)

    response, model = ask_openrouter("2+2")
    assert response == "4"
    assert model


def test_ask_openrouter_falls_back_on_unavailable_model(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)

    def fake_get(*_args, **_kwargs):
        return MockResponse(
            200,
            {
                "data": [
                    {"id": "meta-llama/llama-3.3-8b-instruct:free"},
                    {"id": "openai/gpt-oss-20b:free"},
                ]
            },
        )

    monkeypatch.setattr(httpx, "get", fake_get)

    call_count = {"count": 0}

    def fake_post(*_args, **kwargs):
        model = kwargs["json"]["model"]
        call_count["count"] += 1

        if model == "meta-llama/llama-3.3-8b-instruct:free":
            return MockResponse(
                404,
                text='{"error":{"message":"No endpoints found for meta-llama/llama-3.3-8b-instruct:free."}}',
            )

        return MockResponse(
            200,
            {
                "choices": [
                    {
                        "message": {
                            "content": "4",
                        }
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)

    response, model = ask_openrouter("2+2")
    assert response == "4"
    assert model == "openai/gpt-oss-20b:free"
    assert call_count["count"] >= 1


def test_ai_connectivity_endpoint_missing_key_returns_500(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PM_DB_PATH", str(tmp_path / "ai-missing-key.db"))
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with TestClient(app) as client:
        response = client.post("/api/ai/test", cookies={"pm_auth": "1"})

    assert response.status_code == 500


def test_ai_connectivity_endpoint_success(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PM_DB_PATH", str(tmp_path / "ai-success.db"))
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    def fake_post(*_args, **_kwargs):
        return MockResponse(
            200,
            {
                "choices": [
                    {
                        "message": {
                            "content": "4",
                        }
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)

    with TestClient(app) as client:
        response = client.post("/api/ai/test", cookies={"pm_auth": "1"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["prompt"] == "2+2"
    assert payload["response"] == "4"
