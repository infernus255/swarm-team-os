from __future__ import annotations

import json
from typing import Any, Dict, Set

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel


class WSMessage(BaseModel):
    type: str  # transition | error | log | state_update
    data: Dict[str, Any]


class ConnectionManager:
    def __init__(self) -> None:
        self.active: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self.active.discard(ws)

    async def broadcast(self, message: WSMessage) -> None:
        payload = message.model_dump_json()
        dead: list[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active.discard(ws)


manager = ConnectionManager()


async def swarm_websocket(ws: WebSocket) -> None:
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            await manager.broadcast(
                WSMessage(type="log", data={"from": "client", "message": msg})
            )
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception:
        manager.disconnect(ws)
