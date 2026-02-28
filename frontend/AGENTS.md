# Frontend agent guide

## Purpose

This folder contains the existing frontend MVP for the Project Management app.
It is a Next.js app using the App Router and currently runs as a frontend-only Kanban demo.

## Current behavior

- The route `/` renders a single Kanban board UI
- The board has 5 columns and seeded sample cards
- Users can:
  - Rename column titles inline
  - Add cards to any column
  - Remove cards
  - Drag and drop cards within and across columns
- State is client-side in React state only (no backend persistence yet)

## Key files

- `src/app/page.tsx`: entry page rendering `KanbanBoard`
- `src/components/KanbanBoard.tsx`: board container, local state, DnD context, handlers
- `src/components/KanbanColumn.tsx`: column UI, editable title, card list, add-card form
- `src/components/KanbanCard.tsx`: sortable card UI with remove action
- `src/components/KanbanCardPreview.tsx`: drag overlay preview
- `src/components/NewCardForm.tsx`: inline add-card form
- `src/lib/kanban.ts`: core board types, seed data, card move logic, id creation
- `src/app/globals.css`: theme tokens and global styling

## Libraries and tooling

- Framework: Next.js 16 (React 19)
- Drag-and-drop: `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`
- Styling: Tailwind CSS v4 + CSS variables
- Unit tests: Vitest + Testing Library
- E2E tests: Playwright

## Commands

- Install: `npm install`
- Dev server: `npm run dev`
- Unit tests: `npm run test:unit`
- E2E tests: `npm run test:e2e`
- Full tests: `npm run test:all`

## Implementation notes for agents

- Keep this frontend simple; avoid adding features not requested in `docs/PLAN.md`
- Preserve existing color tokens and design language from `src/app/globals.css`
- Prefer updating shared logic in `src/lib/kanban.ts` instead of duplicating behavior in components
- Maintain and extend tests alongside behavior changes
- Any backend integration should keep the UX stable unless a plan step explicitly changes UX