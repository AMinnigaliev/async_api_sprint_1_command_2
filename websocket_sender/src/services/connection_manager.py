import asyncio
from typing import Dict, Set
from fastapi import WebSocket

class _ConnectionManager:
    def __init__(self):
        self._active: Dict[str, Set[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self._active.setdefault(user_id, set()).add(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket):
        conns = self._active.get(user_id)
        if conns:
            conns.discard(websocket)
            if not conns:
                self._active.pop(user_id)

    async def send_personal_message(self, user_id: str, message: str):
        conns = self._active.get(user_id, set())
        dead = []
        for ws in conns:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)

manager = _ConnectionManager()

async def push_to_user(user_id: str, html_body: str):
    """Отправка html-фрагмента конкретному пользователю."""
    await manager.send_personal_message(user_id, html_body)
