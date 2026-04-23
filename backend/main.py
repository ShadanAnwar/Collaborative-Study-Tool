import json
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

load_dotenv()

from .database import engine, get_db
from . import models
from .routers import auth, rooms, tasks, files
from .websocket.manager import manager

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Collaborative Study Tool", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(tasks.router)
app.include_router(files.router)

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")


@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))


@app.get("/dashboard", include_in_schema=False)
def serve_dashboard():
    return FileResponse(os.path.join(frontend_path, "dashboard.html"))


@app.get("/room", include_in_schema=False)
def serve_room():
    return FileResponse(os.path.join(frontend_path, "room.html"))


# ── WebSocket ─────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


async def get_ws_user(token: str, db: Session) -> models.User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise Exception("User not found")
        return user
    except (JWTError, Exception):
        raise HTTPException(status_code=401, detail="Invalid token")


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    try:
        user = await get_ws_user(token, db)
    except Exception:
        await websocket.close(code=4001)
        return

    # Check membership
    member = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == user.id,
    ).first()
    if not member:
        await websocket.close(code=4003)
        return

    user_info = {"id": user.id, "username": user.username}
    await manager.connect(websocket, room_id, user_info)

    # Notify others someone joined
    await manager.broadcast(room_id, {
        "type": "system",
        "content": f"{user.username} joined the room",
        "time": datetime.utcnow().isoformat(),
        "online": manager.get_online_users(room_id),
    })

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type")

            if msg_type == "chat":
                content = data.get("content", "").strip()
                if not content:
                    continue
                # Persist message
                message = models.Message(
                    room_id=room_id,
                    user_id=user.id,
                    content=content,
                )
                db.add(message)
                db.commit()
                db.refresh(message)

                await manager.broadcast(room_id, {
                    "type": "chat",
                    "user": user.username,
                    "user_id": user.id,
                    "content": content,
                    "time": message.created_at.isoformat(),
                })

            elif msg_type == "task_update":
                task_id = data.get("task_id")
                status = data.get("status")
                task = db.query(models.Task).filter(
                    models.Task.id == task_id,
                    models.Task.room_id == room_id,
                ).first()
                if task and status in ("todo", "inprogress", "done"):
                    task.status = status
                    db.commit()
                    await manager.broadcast(room_id, {
                        "type": "task_update",
                        "task_id": task_id,
                        "status": status,
                        "moved_by": user.username,
                    })

            elif msg_type == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(room_id, {
            "type": "system",
            "content": f"{user.username} left the room",
            "time": datetime.utcnow().isoformat(),
            "online": manager.get_online_users(room_id),
        })
