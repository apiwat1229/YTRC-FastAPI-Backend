from typing import Any

import socketio

from app.core.config import settings

# Create Async Socket.io server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.cors_origins if settings.cors_origins else "*",
)

# Create ASGI application
socket_app = socketio.ASGIApp(
    socketio_server=sio,
    socketio_path="socket.io",
)


@sio.event
async def connect(sid: str, environ: Any) -> None:
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid: str) -> None:
    print(f"Client disconnected: {sid}")


async def broadcast_notification(user_id: str, event: str, data: dict) -> None:
    """
    Broadcast a notification to a specific user.
    """
    # In a real implementation, you would map user_id to sid
    # For now, we'll emit to a room named after the user_id
    await sio.emit(event, data, room=user_id)


async def emit_to_all(event: str, data: dict) -> None:
    """
    Emit an event to all connected clients.
    """
    await sio.emit(event, data)
