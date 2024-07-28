from fastapi import APIRouter, WebSocket
import asyncio
from datetime import datetime

from starlette.websockets import WebSocketDisconnect

router = APIRouter(prefix="/websocket", tags=['websocket'])


@router.websocket("/timer")
async def websocket_timer(websocket: WebSocket):
    """Отправляет текущее время каждую секунду"""
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(1)
            await websocket.send_text(f"Текущее время: {datetime.now().strftime('%H:%M:%S')}")

    except WebSocketDisconnect:
        print("Клиент отключился")