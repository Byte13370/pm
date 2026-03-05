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

- [x] Add frontend API client for board fetch/update
- [x] Load initial board from backend after auth
- [x] Persist user actions (rename/add/delete/move) through backend API
- [x] Add loading/error states with minimal UX impact
- [x] Keep UI interactions responsive and consistent

### Tests

- [x] Unit tests for API client and state adapters
- [x] Integration tests for UI actions triggering API updates
- [x] E2E test confirms board changes persist after reload

### Success criteria

- Frontend reflects backend board state reliably
- Mutations persist and survive page refresh/restart
- Integration tests verify end-to-end board persistence

## Part 8: AI connectivity (OpenRouter)

### Scope

Enable backend AI call through OpenRouter and verify baseline connectivity.

### Checklist

- [x] Add backend OpenRouter client configuration via environment variable
- [x] Configure model to a free OpenRouter model (per user constraint)
- [x] Implement minimal backend function to send a prompt
- [x] Add test route/diagnostic path for connectivity check
- [x] Keep key in local `.env` only

### Tests

- [x] Connectivity check using prompt `2+2`
- [x] Validate non-empty model response and expected semantic answer (`4`)
- [x] Verify graceful error handling for missing/invalid key

### Success criteria

- Backend can successfully call OpenRouter with configured free model
- Connectivity test is repeatable locally
- Secrets are not hardcoded in source

## Part 9: AI structured board assistant backend

### Scope

Send board JSON + user message + history to model and receive structured output with optional board updates.

### Checklist

- [x] Define structured output schema (assistant message + optional board patch/full board)
- [x] Implement prompt construction including board JSON and conversation history
- [x] Validate model output against schema
- [x] Apply optional board update transactionally when valid
- [x] Return assistant reply and new board state to caller

### Tests

- [x] Unit tests for schema validation and parser behavior
- [x] Unit tests for board update application logic
- [x] Backend tests for no-update vs update responses
- [x] Failure-path tests for malformed model outputs

### Success criteria

- AI responses are machine-validated before use
- Board updates are applied safely and deterministically
- API returns consistent structured payloads

## Part 10: Sidebar AI chat UI + auto-refresh

### Scope

Add sidebar chat UX and wire it to AI backend responses, updating board when AI changes it.

### Checklist

- [x] Add sidebar chat component to existing layout
- [x] Support conversation history rendering and input submission
- [x] Call backend AI endpoint with message/history
- [x] Render assistant response in chat stream
- [x] When response includes board update, refresh/apply board state automatically
- [x] Keep UX aligned with existing style system

### Tests

- [x] Component tests for sidebar input and message rendering
- [x] Integration tests for AI request/response lifecycle
- [x] Integration tests for board auto-refresh on AI update
- [x] E2E happy path: ask AI to update a card and verify board updates

### Success criteria

- Sidebar chat works end-to-end with backend AI route
- AI-originated board updates appear in UI without manual reload
- Core chat + board flows are covered by automated tests

## Part 11: Real signup + Supabase Auth + Supabase Postgres

### Scope

Replace fake sign-in with real signup/login via Supabase Auth and move persistence from local SQLite to Supabase Postgres while keeping backend API contracts stable.

### Checklist

- [ ] Add Supabase project configuration and environment variables for frontend and backend
- [ ] Add frontend signup/login flow using `@supabase/supabase-js`
- [ ] Replace cookie-based fake auth with bearer-token auth from Supabase session
- [ ] Verify Supabase JWT on backend using JWKS and extract authenticated user identity
- [ ] Replace SQLite repository with Postgres repository against Supabase database
- [ ] Add backend user upsert keyed by Supabase user id (`sub`) and one-board-per-user mapping
- [ ] Keep `/api/board` and `/api/ai/chat` request/response contracts unchanged for UI compatibility
- [ ] Update docker/local startup docs for Supabase-backed configuration
- [ ] Replace auth/db tests and add signup/login integration coverage

### Tests

- [ ] Backend unit tests for token parsing and JWT validation error paths
- [ ] Backend repository tests for board read/write with Postgres upsert semantics
- [ ] API tests for unauthorized, authorized, and first-login user bootstrap flows
- [ ] Frontend unit tests for signup/login/logout states using mocked Supabase client
- [ ] E2E: signup new user, create/move card, reload confirms persistence

### Success criteria

- User can sign up and sign in with Supabase credentials
- Backend only serves board/AI routes for valid Supabase-authenticated users
- Board data persists in Supabase Postgres and survives restart/redeploy
- Existing Kanban + AI UX remains functional without endpoint contract changes

## Approval gate

Implementation should proceed part-by-part and pause at key approval gates:

- [x] Approval after Part 1 (this plan)
- [x] Approval after Part 5 (database design)
- [ ] Approval after Part 11 design review (auth + Supabase integration)