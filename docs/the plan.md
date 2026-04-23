# Collaborative Study Tool — Build Plan

## Overview

A clean, Asana-inspired study room app with real-time collaboration. One codebase, minimal dependencies, no over-engineering.

---

## Tech Stack (Simplified)

| Layer | Choice | Why |
|---|---|---|
| Backend | FastAPI + Python | Fast, async, WebSocket native |
| Database | SQLite → PostgreSQL | SQLite for dev, easy upgrade |
| Auth | JWT (PyJWT) | Simple, stateless |
| Frontend | HTML + Tailwind + Vanilla JS | No build step, clean, fast |
| Real-time | FastAPI WebSockets | Built-in, no extra service |
| File Storage | Local disk (`/uploads`) | Simple, no cloud needed |

---

## Project Structure

```
study-tool/
├── backend/
│   ├── main.py                  # App entry point
│   ├── database.py              # DB connection
│   ├── models.py                # SQLAlchemy models
│   ├── schemas.py               # Pydantic schemas
│   ├── auth.py                  # JWT logic
│   ├── routers/
│   │   ├── auth.py              # /api/auth/*
│   │   ├── rooms.py             # /api/rooms/*
│   │   ├── tasks.py             # /api/tasks/*
│   │   └── files.py             # /api/files/*
│   ├── websocket/
│   │   └── manager.py           # WS connection manager
│   └── uploads/                 # File storage
│
├── frontend/
│   ├── index.html               # Login / Register
│   ├── dashboard.html           # Rooms list
│   ├── room.html                # Room: chat + kanban + files
│   └── assets/
│       ├── app.js               # Shared JS logic
│       ├── kanban.js            # Drag-and-drop board
│       └── chat.js              # WebSocket chat client
│
├── requirements.txt
├── .env
└── README.md
```

---

## Database Schema

5 tables, clean and minimal.

```
Users         → id, username, email, hashed_password, created_at
Rooms         → id, name, description, owner_id, created_at
RoomMembers   → id, room_id, user_id, role (admin/member)
Tasks         → id, room_id, title, status (todo/inprogress/done),
                assigned_to, created_by, created_at
Messages      → id, room_id, user_id, content, created_at
Files         → id, room_id, uploaded_by, filename, filepath, created_at
```

---

## API Endpoints

### Auth
- `POST /api/auth/register`
- `POST /api/auth/login` → returns JWT token

### Rooms
- `GET /api/rooms` — list my rooms
- `POST /api/rooms` — create room
- `POST /api/rooms/{id}/join` — join with invite code
- `GET /api/rooms/{id}/members`

### Tasks
- `GET /api/rooms/{id}/tasks`
- `POST /api/rooms/{id}/tasks`
- `PATCH /api/tasks/{id}` — update status / title
- `DELETE /api/tasks/{id}`

### Files
- `POST /api/rooms/{id}/files` — upload
- `GET /api/rooms/{id}/files` — list
- `GET /api/files/{id}/download`

### WebSocket
- `WS /ws/{room_id}?token=...` — handles chat messages + live task updates in one connection

---

## Frontend Pages (3 screens only)

### Screen 1 — Login/Register (`index.html`)
Simple centered card, email + password, JWT stored in `localStorage`.

### Screen 2 — Dashboard (`dashboard.html`)
Mirrors the Asana-style reference UI:
- Left sidebar: My Rooms list (colored dots like the project list)
- Main area: Room cards in a grid
- "Create Room" / "Join Room" buttons

### Screen 3 — Room (`room.html`)
Three-panel layout:
- **Left**: Member list + file uploads
- **Center**: Kanban board (3 columns: To-Do / In Progress / Done) — drag-and-drop with vanilla JS
- **Right**: Real-time chat panel

---

## WebSocket Message Protocol

Simple JSON — one WS connection per room handles everything, no separate channels needed.

```json
// Chat message (client → server)
{ "type": "chat", "content": "Hello!" }

// Task moved (client → server)
{ "type": "task_update", "task_id": 5, "status": "done" }

// Server broadcast to room
{ "type": "chat", "user": "Ryan", "content": "Hello!", "time": "..." }
{ "type": "task_update", "task_id": 5, "status": "done", "moved_by": "Ryan" }
```

---

## Activity Tracking (Lightweight)

No separate table needed — derived from existing data:

- **Messages sent** → `COUNT` from Messages table per user per room
- **Tasks completed** → `COUNT WHERE status='done' AND assigned_to=user`
- Shown as a small stats strip on the dashboard

---

## Build Order (Phases)

| Phase | What | Complexity |
|---|---|---|
| 1 | Backend: models, DB, auth endpoints | Low |
| 2 | Backend: rooms + tasks REST APIs | Low |
| 3 | Backend: WebSocket manager + file upload | Medium |
| 4 | Frontend: Login + Dashboard UI | Low |
| 5 | Frontend: Kanban board + drag-and-drop | Medium |
| 6 | Frontend: Chat + WS client | Medium |
| 7 | Wire everything together + test | Low |

---

## Setup Instructions

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env:
# DATABASE_URL=sqlite:///./study.db
# SECRET_KEY=your-secret-key

# 3. Run the server
uvicorn backend.main:app --reload

# 4. Open the app
open frontend/index.html
```

> No Docker, no complex setup — just Python + a browser.

---

## Key Design Decisions

| Decision | Reasoning |
|---|---|
| No React | Vanilla JS is enough — no build toolchain needed |
| SQLite first | Works out of the box; swap to Postgres with one env var change |
| One WebSocket per room | Handles both chat and task updates — no pub/sub system required |
| Local file storage | No S3/cloud; files saved to `/uploads` folder |
| Tailwind via CDN | No npm, no bundler |

---

> Ready to start? Say **"start Phase 1"** to begin the backend foundation, or request changes to the plan first.
