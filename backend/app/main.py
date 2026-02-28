from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi import Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.auth import require_authenticated_username
from app.db import get_board_for_username, initialize_database, replace_board_for_username
from app.schemas import BoardData


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="PM MVP Backend", version="0.1.0", lifespan=lifespan)

STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/hello")
def hello() -> dict[str, str]:
    return {"message": "Hello from FastAPI"}


@app.get("/api/board", response_model=BoardData)
def get_board(username: str = Depends(require_authenticated_username)) -> BoardData:
    try:
        board_data = get_board_for_username(username)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return BoardData.model_validate(board_data)


@app.put("/api/board", response_model=BoardData)
def update_board(
    board: BoardData,
    username: str = Depends(require_authenticated_username),
) -> BoardData:
    try:
        updated = replace_board_for_username(username, board.model_dump())
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return BoardData.model_validate(updated)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root() -> Response:
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)

    return HTMLResponse(
        "Frontend build not found. Build and copy static assets to backend/app/static.",
        status_code=503,
    )


app.mount(
    "/",
    StaticFiles(directory=STATIC_DIR, html=True, check_dir=False),
    name="frontend-static",
)
