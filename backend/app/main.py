from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi import Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.ai import connectivity_test
from app.ai_chat import run_structured_board_assistant
from app.auth import require_authenticated_username
from app.db import get_board_for_username, initialize_database, replace_board_for_username
from app.schemas import AIChatRequest, AIChatResponse, BoardData


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


@app.post("/api/ai/test")
def ai_connectivity_test(
    username: str = Depends(require_authenticated_username),
) -> dict[str, str]:
    _ = username

    try:
        return connectivity_test()
    except RuntimeError as exc:
        message = str(exc)
        if "OPENROUTER_API_KEY" in message:
            raise HTTPException(status_code=500, detail=message) from exc
        raise HTTPException(status_code=502, detail=message) from exc


@app.post("/api/ai/chat", response_model=AIChatResponse)
def ai_chat(
    payload: AIChatRequest,
    username: str = Depends(require_authenticated_username),
) -> AIChatResponse:
    try:
        current_board = BoardData.model_validate(get_board_for_username(username))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        structured, model = run_structured_board_assistant(
            question=payload.question,
            board=current_board,
            history=payload.history,
        )
    except RuntimeError as exc:
        message = str(exc)
        if "OPENROUTER_API_KEY" in message:
            raise HTTPException(status_code=500, detail=message) from exc
        raise HTTPException(status_code=502, detail=message) from exc

    board_to_return = current_board
    board_updated = False

    if structured.board_update is not None:
        persisted = replace_board_for_username(username, structured.board_update.model_dump())
        board_to_return = BoardData.model_validate(persisted)
        board_updated = True

    return AIChatResponse(
        model=model,
        assistant_response=structured.assistant_response,
        board_updated=board_updated,
        board=board_to_return,
    )


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
