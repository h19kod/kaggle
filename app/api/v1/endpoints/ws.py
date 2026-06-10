import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.core.redis_client import get_redis
from app.core.database import get_db
from app.core.docker_sandbox import get_sandbox
from app.api.deps import get_current_active_user
from app.crud.notebook import notebook_crud, compute_session_crud
from app.models.user import User

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            self.active_connections[channel].remove(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]

    async def broadcast(self, channel: str, message: dict):
        if channel in self.active_connections:
            disconnected = []
            for ws in self.active_connections[channel]:
                try:
                    await ws.send_json(message)
                except Exception:
                    disconnected.append(ws)
            for ws in disconnected:
                self.disconnect(ws, channel)


manager = ConnectionManager()


@router.websocket("/leaderboard/{competition_id}")
async def leaderboard_ws(websocket: WebSocket, competition_id: int):
    channel = f"leaderboard:{competition_id}"
    await manager.connect(websocket, channel)
    redis_client = get_redis()
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel)
    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message and message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_json(data)
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
        pubsub.unsubscribe(channel)


@router.websocket("/notebooks/{notebook_id}/execute")
async def notebook_execute_ws(
    websocket: WebSocket,
    notebook_id: int,
    db: Session = Depends(get_db),
):
    from app.crud.notebook import compute_session_crud
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            action = msg.get("action")
            if action == "run":
                code = msg.get("code", "")
                sessions = compute_session_crud.get_by_notebook(db, notebook_id=notebook_id)
                active = [s for s in sessions if s.session_status.value == "Active" and s.container_id]
                if not active:
                    await websocket.send_json({"type": "error", "message": "No active compute session. Start a session first."})
                    continue
                container_id = active[-1].container_id
                try:
                    output = await asyncio.to_thread(get_sandbox().exec_code, container_id, code)
                    await websocket.send_json({"type": "output", "output": output})
                except Exception as exc:
                    await websocket.send_json({"type": "error", "message": str(exc)})
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
