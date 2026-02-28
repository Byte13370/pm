# Backend agent guide

## Purpose

This folder contains the FastAPI backend for the Project Management MVP.

## Current implementation (Part 2)

- FastAPI app entrypoint: `app/main.py`
- Routes:
	- `GET /` returns a simple hello-world HTML page
	- `GET /api/health` returns service status
	- `GET /api/hello` returns sample JSON for API validation
- Python dependencies managed via `uv` and `pyproject.toml`

## Docker

- Dockerfile: `backend/Dockerfile`
- Uses Python 3.12 slim
- Installs dependencies with `uv`
- Runs server with `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## Implementation notes for agents

- Keep backend changes minimal and aligned with `docs/PLAN.md`
- Add tests as parts require; avoid adding unrequested features
- Keep API contracts explicit and small