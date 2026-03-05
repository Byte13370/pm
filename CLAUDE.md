# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Kanban Studio** is a project management MVP featuring a drag-and-drop Kanban board with an AI sidebar chat assistant. Users sign in to access their board, which persists to a database. The AI can view board state and make structural changes (create/edit/move cards).

**Technology Stack:**
- Frontend: Next.js 16 + React 19 + TypeScript + Tailwind CSS + @dnd-kit (drag-drop)
- Backend: FastAPI + Python 3.12+ + SQLite (local) / Postgres (Supabase)
- Auth: Supabase JWT (production) / cookie-based fallback (development)
- AI: OpenRouter API with structured output validation
- Deployment: Docker container (docker-compose.yml for local development)

## High-Level Architecture

### Frontend (Next.js)
- **Entry**: `frontend/src/app/page.tsx` → wraps app in `AuthGate` (login/board gate)
- **Authentication**: `AuthGate.tsx` handles login UI (hardcoded `user`/`password` in MVP) and routes to board
- **Board State**: `KanbanBoard.tsx` manages columns/cards, calls backend `/api/board` to fetch/persist
- **AI Chat**: `AIChatSidebar.tsx` sidebar with message history, calls `/api/ai/chat`, applies board updates from AI responses
- **API Client**: `lib/boardApi.ts` wraps fetch calls with authentication; `lib/auth.ts` manages session

### Backend (FastAPI)
- **Main Server**: `backend/app/main.py` defines routes and mounts static frontend
- **Authentication**: `backend/app/auth.py` verifies Supabase JWT or fallback cookie auth
- **Database**: `backend/app/db.py` handles SQLite/Postgres abstraction; initializes schema on startup
- **AI Integration**: `backend/app/ai.py` (connectivity test), `backend/app/ai_chat.py` (structured assistant)
- **Schemas**: `backend/app/schemas.py` defines Pydantic models (BoardData, AIChatRequest, AIChatResponse)
- **Static Serving**: Frontend build output (Next.js static export) served from `backend/app/static/`

### Database Schema (Part 5 / 11)

**SQLite (Local MVP):**
```
users (id, username, created_at, updated_at)
boards (id, user_id→UNIQUE, board_json, version, created_at, updated_at)
```

**Postgres (Supabase Production - Part 11):**
```
users (id, supabase_user_id→UNIQUE, email, created_at, updated_at)
boards (id, user_id→UNIQUE REFERENCES users, board_json, version, created_at, updated_at)
```

Board JSON structure (same for both):
```json
{
  "columns": [{"id": "col-*", "title": "...", "cardIds": ["card-1", "card-2"]}],
  "cards": {"card-1": {"id": "card-1", "title": "...", "details": "..."}}
}
```

## Common Development Commands

### Frontend
```bash
cd frontend

# Development
npm run dev                    # Start Next.js dev server (localhost:3000)
npm run build                  # Build static export to .next/

# Testing
npm run test:unit             # Run Vitest (single run)
npm run test:unit:watch       # Run Vitest in watch mode
npm run test:e2e              # Run Playwright E2E tests
npm run test:all              # Run all tests

# Linting
npm run lint                  # Run ESLint
```

### Backend
```bash
cd backend

# Setup (one-time)
uv pip install -e .           # Install dependencies in editable mode (uv required)

# Development
uv run uvicorn app.main:app --reload --port 8000    # Start server with auto-reload

# Testing
uv run pytest                 # Run all tests
uv run pytest tests/ -v       # Verbose test output
uv run pytest -k test_name    # Run specific test by name
```

### Full Stack (Docker)
```bash
# Build and run containerized app
docker-compose up --build

# Access:
# - Frontend: http://localhost:80
# - Backend API: http://localhost/api/*
```

### Scripts
```bash
# Start/stop scripts in scripts/ for Mac, Linux, Windows
# These manage Docker containers for local development
```

## API Contracts

### Authentication
- **Development**: Cookie `pm_auth=1` or Bearer token
- **Production**: Supabase JWT in `Authorization: Bearer <token>` header
- **Backend validation**: `auth.py:require_authenticated_user` dependency

### Key Routes
```
GET  /api/health              # Health check (no auth needed)
GET  /api/board               # Get user's board (JSON) [AUTH]
PUT  /api/board               # Update user's board [AUTH]
POST /api/ai/chat             # Send message + history, get AI response + optional board update [AUTH]
POST /api/ai/test             # Test OpenRouter connectivity [AUTH]
GET  /                        # Serve frontend (static HTML/JS)
```

**Request/Response Models** (`schemas.py`):
- `BoardData`: `{columns: [...], cards: {...}}`
- `AIChatRequest`: `{question: str, history: [...{role, content}]}`
- `AIChatResponse`: `{model: str, assistant_response: str, board_updated: bool, board: BoardData}`

## Configuration & Environment Variables

### Backend
```
# Database (one required)
PM_DB_PATH=/path/to/pm.db              # SQLite path (optional, defaults to backend/data/pm.db)
SUPABASE_DB_URL=postgres://...         # Postgres connection (if set, uses Supabase)

# Supabase Auth (if using Supabase)
SUPABASE_URL=https://...               # Supabase project URL
SUPABASE_JWKS_URL=...                  # Optional explicit JWKS endpoint

# AI
OPENROUTER_API_KEY=...                 # OpenRouter API key (required for AI features)
```

### Frontend
```
NEXT_PUBLIC_SUPABASE_URL=...           # Supabase URL (optional, for future signup UI)
NEXT_PUBLIC_SUPABASE_ANON_KEY=...      # Supabase anon key (optional)
```

## Key Implementation Details

### Authentication Flow (Current)
1. **Development**: User submits login form with username/password (dummy validation in `AuthGate.tsx`)
2. Frontend sets cookie `pm_auth=1` on success
3. Backend middleware (`auth.py:require_authenticated_user`) checks cookie or Bearer token
4. Authenticated requests resolve to `AuthenticatedUser(sub, email)` for database lookups

### Supabase Auth Flow (Part 11 - In Progress)
1. Frontend calls Supabase Auth for signup/login, receives JWT
2. Frontend stores JWT in Supabase session (automatic with `@supabase/supabase-js`)
3. Frontend sends JWT in `Authorization: Bearer <token>` header
4. Backend verifies JWT signature and issuer, extracts `sub` (user ID)
5. Backend upserts user in Postgres on first request

### Board Persistence
1. **Read**: `GET /api/board` → backend loads JSON from DB → frontend renders in `KanbanBoard.tsx`
2. **Write**: User drags card → `KanbanBoard` updates local state → calls `PUT /api/board` → backend persists and returns updated board
3. **AI Update**: AI response includes optional `board_update` → frontend applies to local state and syncs via `PUT /api/board`

### AI Integration (Part 9-10)
1. User sends message in `AIChatSidebar.tsx`
2. `POST /api/ai/chat` with `{question, history, board}`
3. `ai_chat.py:run_structured_board_assistant` constructs prompt with board JSON + history
4. OpenRouter returns JSON: `{assistant_response, board_update?: {columns, cards}}`
5. Frontend renders response in chat and applies board update if present
6. Backend persists board update automatically

## Frontend Component Structure

- `AuthGate.tsx`: Top-level gate (login form vs board)
- `KanbanBoard.tsx`: Main board state, column/card rendering
- `KanbanColumn.tsx`: Single column with drag-drop zone
- `KanbanCard.tsx`: Card with edit modal
- `NewCardForm.tsx`: Add card form
- `AIChatSidebar.tsx`: Chat UI with message history and input

**State Management**: React hooks (no Redux). Board state in `KanbanBoard`, chat history in `AIChatSidebar`. API calls via `boardApi.ts` helper.

## Backend Module Structure

- `main.py`: FastAPI app, route definitions, static file mounting, lifespan hook
- `auth.py`: JWT verification, fallback auth, `AuthenticatedUser` dataclass
- `db.py`: Database initialization, board CRUD, SQLite/Postgres abstraction
- `ai_chat.py`: Prompt construction, OpenRouter call, structured output parsing
- `ai.py`: Connectivity test, error handling
- `schemas.py`: Pydantic models for request/response validation

## Testing Strategy

### Frontend
- **Unit tests** (`*.test.ts(x)`): Component rendering, hooks, utility functions with Vitest + React Testing Library
- **E2E tests** (`playwright.config.ts`): Full user flows (login, board interactions) with Playwright

### Backend
- **Unit tests** (`tests/`): Database operations, auth parsing, AI schema validation with pytest
- **Integration tests**: API routes with mocked dependencies

## Development Workflow

1. **Local setup**: `npm install` (frontend), `uv sync` or `pip install -e .` (backend)
2. **Run dev servers**: `npm run dev` (frontend), `uv run uvicorn...` (backend in separate terminal)
3. **Or Docker**: `docker-compose up --build` (all-in-one)
4. **Tests**: Run `npm run test:unit` and `uv run pytest` as you develop
5. **Frontend build**: `npm run build` generates static output → copies to `backend/app/static/` for Docker

## Debugging Tips

- **Auth failures**: Check `auth.py` - verify JWT issuer, `SUPABASE_URL`, or cookie presence
- **Board not loading**: Inspect `/api/board` response in Network tab; check database initialization logs
- **AI not responding**: Verify `OPENROUTER_API_KEY` set; test with `POST /api/ai/test`
- **Database errors**: Check `db.py` initialization logic; confirm `SUPABASE_DB_URL` or SQLite path
- **CORS issues**: Backend routes require same-origin frontend or explicit CORS (currently same-origin via static mounting)

## Color Scheme (Brand)

- Accent Yellow: `#ecad0a`
- Blue Primary: `#209dd7`
- Purple Secondary: `#753991`
- Dark Navy: `#032147`
- Gray Text: `#888888`

## Project Status

- **Completed**: Parts 1-10 (scaffolding, frontend integration, auth, persistence, AI chat)
- **In Progress**: Part 11 (Supabase Auth + Postgres migration)
- **Next**: Migrate from local SQLite + dummy auth to Supabase-backed signup/login

See `docs/PLAN.md` for full part-by-part breakdown and approval gates.
