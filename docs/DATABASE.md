# Database design for Kanban persistence (Part 5)

## Scope

This document proposes the SQLite schema and persistence approach for the MVP.

MVP constraints:

- Dummy login only (`user` / `password`)
- One Kanban board per signed-in user
- Data stored as JSON for board state
- Design must support future multi-user expansion

## Proposed database

- Engine: SQLite
- DB file: `backend/data/pm.db` (created automatically if missing)

## Schema

### `users`

Purpose: store app users (MVP starts with one seeded user).

```sql
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### `boards`

Purpose: store one board JSON document per user.

```sql
CREATE TABLE IF NOT EXISTS boards (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL UNIQUE,
  board_json TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

Indexes:

```sql
CREATE INDEX IF NOT EXISTS idx_boards_user_id ON boards(user_id);
```

## JSON structure (`board_json`)

The JSON payload is aligned with current frontend board shape.

```json
{
  "columns": [
    { "id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"] }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "Example card",
      "details": "Example details"
    }
  }
}
```

Notes:

- `columns` order is authoritative for column display order.
- `cardIds` order is authoritative for card order in each column.
- `cards` is a map keyed by card id for fast lookup.

## Initialization and migration strategy

On backend startup:

1. Ensure directory for DB file exists.
2. Open SQLite connection.
3. Run `CREATE TABLE IF NOT EXISTS` statements.
4. Seed MVP user (`username = 'user'`) if absent.
5. Seed default board row for that user if absent.

Migration approach for MVP:

- Start with idempotent SQL migration scripts run in order.
- Use a lightweight `schema_migrations` table later when needed.
- For now, startup initialization can execute schema DDL safely each run.

## Read/write lifecycle

Read board:

1. Resolve user by username (or authenticated user id later).
2. Read `boards.board_json` by `user_id`.
3. Parse JSON and return to API client.

Write board:

1. Validate incoming board payload shape.
2. Serialize payload to JSON string.
3. Update `boards.board_json`, increment `version`, update `updated_at`.
4. Return updated board payload.

## Why this fits MVP and future growth

MVP fit:

- Very simple data model and implementation path.
- Full board updates map cleanly to existing frontend state.

Future fit:

- Multiple users supported via `users` table and `boards.user_id` unique mapping.
- `version` field enables optimistic concurrency later.
- Can evolve to more normalized schema if needed without changing API immediately.

## Validation checklist against requirements

- Supports one board per user for MVP: yes (`boards.user_id UNIQUE`).
- Supports future multi-user: yes (`users` + foreign key relation).
- Matches current frontend board model: yes (columns + cards JSON shape).

## Part 11 migration target: Supabase Postgres

For real signup, auth and persistence move to Supabase services:

- Auth: Supabase Auth (email/password signup + login)
- Database: Supabase Postgres (replacing local SQLite)
- API ownership: FastAPI remains source of truth for board and AI routes

### Target schema (Postgres)

```sql
CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  supabase_user_id UUID NOT NULL UNIQUE,
  email TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS boards (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  board_json JSONB NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_supabase_user_id ON users (supabase_user_id);
CREATE INDEX IF NOT EXISTS idx_boards_user_id ON boards (user_id);
```

### Identity mapping

- Backend verifies Supabase JWT and uses the token `sub` claim as canonical user identity.
- `sub` maps to `users.supabase_user_id`.
- `email` claim is optional and stored if present.

### Runtime read/write lifecycle (Supabase)

1. Frontend sends `Authorization: Bearer <access_token>` to backend API.
2. Backend verifies token signature and claims against Supabase JWKS.
3. Backend upserts `users` row by `supabase_user_id` on first authenticated request.
4. Board read: lookup by `users.id` and return parsed `board_json`.
5. Board write: upsert `boards` by `user_id`, increment `version`, set `updated_at`.

### Environment variables

Backend:

- `SUPABASE_URL` (for JWKS URL derivation if needed)
- `SUPABASE_JWKS_URL` (explicit JWKS endpoint)
- `SUPABASE_DB_URL` (Postgres connection string)

Frontend:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### Migration policy for this rollout

- No migration from existing SQLite data.
- Fresh Supabase Postgres data store for signup rollout.
- SQLite startup initialization remains only until Part 11 backend switch is complete, then removed.