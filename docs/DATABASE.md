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