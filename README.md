# 📚 StudySync — Collaborative Study Tool

A real-time collaborative study room app with **Kanban boards**, **live chat**, and **file sharing**.
Built with FastAPI + vanilla JS, no complex build toolchain needed.

## Features

- **🔐 Auth**: Register/login with JWT tokens
- **🏠 Study Rooms**: Create or join rooms with invite codes
- **📋 Kanban Board**: Drag-and-drop task management (To Do → In Progress → Done)
- **💬 Live Chat**: Real-time messaging via WebSocket
- **📁 File Sharing**: Upload and download study materials
- **👥 Members**: See who's online in real-time

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
uvicorn backend.main:app --reload

# 3. Open in browser
# http://127.0.0.1:8000
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Python |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | JWT (python-jose) |
| Frontend | HTML + Tailwind-free CSS + Vanilla JS |
| Real-time | WebSocket |
| File Storage | Local disk |

## Project Structure

```
study-tool/
├── backend/
│   ├── main.py              # App entry + WebSocket handler
│   ├── database.py           # SQLAlchemy setup
│   ├── models.py             # 6 DB models
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── auth.py               # JWT + password hashing
│   ├── routers/
│   │   ├── auth.py           # /api/auth/*
│   │   ├── rooms.py          # /api/rooms/*
│   │   ├── tasks.py          # /api/tasks/*
│   │   └── files.py          # /api/files/*
│   ├── websocket/
│   │   └── manager.py        # WS connection manager
│   └── uploads/              # Uploaded files
│
├── frontend/
│   ├── index.html            # Login / Register
│   ├── dashboard.html        # Room list + stats
│   ├── room.html             # Kanban + Chat + Files
│   └── assets/
│       ├── app.css           # Global styles
│       ├── app.js            # Shared JS utilities
│       ├── kanban.js          # Drag-and-drop board
│       └── chat.js           # WebSocket chat
│
├── requirements.txt
├── .env
└── README.md
```

## API Docs

Once running, visit: **http://127.0.0.1:8000/docs** for interactive Swagger UI.
