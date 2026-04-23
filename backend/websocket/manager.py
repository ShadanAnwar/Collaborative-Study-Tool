from fastapi import WebSocket
from typing import Dict, List
import json


class ConnectionManager:
    def __init__(self):
        # room_id -> list of (websocket, user_info)
        self.active_connections: Dict[int, List[dict]] = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_info: dict):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append({"ws": websocket, "user": user_info})

    def disconnect(self, websocket: WebSocket, room_id: int):
        if room_id in self.active_connections:
            self.active_connections[room_id] = [
                c for c in self.active_connections[room_id] if c["ws"] != websocket
            ]

    async def broadcast(self, room_id: int, message: dict):
        if room_id not in self.active_connections:
            return
        dead = []
        for conn in self.active_connections[room_id]:
            try:
                await conn["ws"].send_text(json.dumps(message))
            except Exception:
                dead.append(conn)
        for d in dead:
            self.active_connections[room_id].remove(d)

    def get_online_users(self, room_id: int) -> List[dict]:
        if room_id not in self.active_connections:
            return []
        return [c["user"] for c in self.active_connections[room_id]]


manager = ConnectionManager()
