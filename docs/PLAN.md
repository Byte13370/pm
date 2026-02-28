# Project plan and execution checklist

This plan turns the high-level parts into concrete execution steps with validation.
Each part includes scope, implementation checklist, tests, and success criteria.

## Part 1: Plan (documentation + approval)

### Scope

Document the detailed project approach and capture a frontend implementation guide.

### Checklist

- [x] Enrich this file with detailed execution steps
- [x] Add tests and success criteria per part
- [x] Create `frontend/AGENTS.md` describing the existing frontend codebase
- [x] Request and receive user approval before starting Part 2

### Tests

- [x] Manual review of `docs/PLAN.md` for completeness
- [x] Manual review of `frontend/AGENTS.md` for accuracy against current code

### Success criteria

- Plan covers Parts 2-10 with actionable checklists
- Every part includes explicit test expectations
- User explicitly approves plan before implementation proceeds

## Part 2: Scaffolding

### Scope

Create containerized app foundation with FastAPI backend and OS start/stop scripts.

### Checklist

- [x] Create backend project scaffold in `backend/` (FastAPI app, routing, config)
- [x] Add Python dependency management via `uv`
- [x] Add Dockerfile and compose config for local run
- [x] Add script files in `scripts/` for Mac, Linux, and Windows start/stop
- [x] Implement `GET /api/health` and one sample API route
- [x] Serve temporary static hello page from backend root `/`
- [x] Document run instructions minimally in README/docs

### Tests

- [x] Build container successfully
- [x] Run container locally and verify root `/` returns hello page
- [x] Verify `GET /api/health` returns healthy response
- [x] Verify sample API route returns expected JSON
- [x] Validate start/stop scripts execute successfully on expected OS shell

### Success criteria

- Single command path exists to start stack locally
- Backend responds on web root and API endpoints in container
- Scripts reliably start and stop local app environment

## Part 3: Add in Frontend

### Scope

Integrate existing Next.js frontend build into backend static serving flow.

### Checklist

- [x] Add frontend static build step
- [x] Wire backend static file hosting for frontend output
- [x] Ensure `/` serves Kanban app instead of placeholder HTML
- [x] Keep existing frontend interactions intact
- [x] Add/adjust integration tests for served frontend

### Tests

- [x] Frontend build succeeds in local and container workflows
- [x] `GET /` serves built frontend assets via backend
- [x] Existing unit tests pass
- [x] Integration/e2e confirms board renders with five columns

### Success criteria

- Frontend is served by backend in Dockerized local environment
- Kanban demo works from backend root route
- Test suite covers static serving path and core UI rendering

## Part 4: Fake user sign-in experience

### Scope

Gate board access behind simple local auth (`user` / `password`) and support logout.

### Checklist

- [x] Add login UI for unauthenticated users at `/`
- [x] Implement dummy credential validation (`user`, `password`)
- [x] Add session mechanism (simple cookie/session token for MVP)
- [x] Protect Kanban route content unless authenticated
- [x] Add logout action clearing session
- [x] Preserve simple UX and avoid extra auth features

### Tests

- [x] Unit tests for auth validation and session helpers
- [x] Integration tests for redirect/guard behavior
- [x] E2E: login success path
- [x] E2E: login failure path
- [x] E2E: logout returns to login screen

### Success criteria

- Unauthenticated access does not show Kanban data
- Valid dummy login grants access to Kanban
- Logout clears auth and requires login again

## Part 5: Database modeling

### Scope

Design schema and persistence strategy for board JSON per user, then get approval.

### Checklist

- [x] Draft SQLite schema for users and board state
- [x] Define JSON structure for board persistence
- [x] Document migration/init strategy if DB file is missing
- [x] Document read/write lifecycle and constraints in `docs/`
- [x] Request user sign-off on schema and docs before implementation

### Tests

- [x] Validate schema supports one board per user for MVP
- [x] Validate schema supports future multi-user extension
- [x] Review docs for clarity and consistency with requirements

### Success criteria

- Clear, approved schema and persistence design exists before coding data layer
- Approach is compatible with current frontend board model

## Part 6: Backend API for Kanban persistence

### Scope

Implement backend routes to read/update board data with SQLite creation on startup if missing.

### Checklist

- [x] Implement DB initialization and auto-create database file
- [x] Add data access layer for board CRUD (MVP: read + replace/update)
- [x] Add authenticated API endpoints for current user board
- [x] Add request/response models and validation
- [x] Add error handling for not found/invalid payload

### Tests

- [x] Backend unit tests for DB initialization and repository logic
- [x] API tests for board read/update flows
- [x] API tests for invalid input handling
- [x] Verify database file auto-creation on clean environment

### Success criteria

- Board state persists in SQLite across app restarts
- API is stable and validated by backend tests
- DB initializes automatically without manual steps

## Part 7: Frontend + Backend integration

### Scope

Switch frontend from in-memory board to backend-driven persistence.

### Checklist

- [ ] Add frontend API client for board fetch/update
- [ ] Load initial board from backend after auth
- [ ] Persist user actions (rename/add/delete/move) through backend API
- [ ] Add loading/error states with minimal UX impact
- [ ] Keep UI interactions responsive and consistent

### Tests

- [ ] Unit tests for API client and state adapters
- [ ] Integration tests for UI actions triggering API updates
- [ ] E2E test confirms board changes persist after reload

### Success criteria

- Frontend reflects backend board state reliably
- Mutations persist and survive page refresh/restart
- Integration tests verify end-to-end board persistence

## Part 8: AI connectivity (OpenRouter)

### Scope

Enable backend AI call through OpenRouter and verify baseline connectivity.

### Checklist

- [ ] Add backend OpenRouter client configuration via environment variable
- [ ] Configure model to a free OpenRouter model (per user constraint)
- [ ] Implement minimal backend function to send a prompt
- [ ] Add test route/diagnostic path for connectivity check
- [ ] Keep key in local `.env` only

### Tests

- [ ] Connectivity check using prompt `2+2`
- [ ] Validate non-empty model response and expected semantic answer (`4`)
- [ ] Verify graceful error handling for missing/invalid key

### Success criteria

- Backend can successfully call OpenRouter with configured free model
- Connectivity test is repeatable locally
- Secrets are not hardcoded in source

## Part 9: AI structured board assistant backend

### Scope

Send board JSON + user message + history to model and receive structured output with optional board updates.

### Checklist

- [ ] Define structured output schema (assistant message + optional board patch/full board)
- [ ] Implement prompt construction including board JSON and conversation history
- [ ] Validate model output against schema
- [ ] Apply optional board update transactionally when valid
- [ ] Return assistant reply and new board state to caller

### Tests

- [ ] Unit tests for schema validation and parser behavior
- [ ] Unit tests for board update application logic
- [ ] Backend tests for no-update vs update responses
- [ ] Failure-path tests for malformed model outputs

### Success criteria

- AI responses are machine-validated before use
- Board updates are applied safely and deterministically
- API returns consistent structured payloads

## Part 10: Sidebar AI chat UI + auto-refresh

### Scope

Add sidebar chat UX and wire it to AI backend responses, updating board when AI changes it.

### Checklist

- [ ] Add sidebar chat component to existing layout
- [ ] Support conversation history rendering and input submission
- [ ] Call backend AI endpoint with message/history
- [ ] Render assistant response in chat stream
- [ ] When response includes board update, refresh/apply board state automatically
- [ ] Keep UX aligned with existing style system

### Tests

- [ ] Component tests for sidebar input and message rendering
- [ ] Integration tests for AI request/response lifecycle
- [ ] Integration tests for board auto-refresh on AI update
- [ ] E2E happy path: ask AI to update a card and verify board updates

### Success criteria

- Sidebar chat works end-to-end with backend AI route
- AI-originated board updates appear in UI without manual reload
- Core chat + board flows are covered by automated tests

## Approval gate

Implementation should proceed part-by-part and pause at key approval gates:

- [x] Approval after Part 1 (this plan)
- [x] Approval after Part 5 (database design)