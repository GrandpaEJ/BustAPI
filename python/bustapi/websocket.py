"""
WebSocket support for BustAPI.

Provides high-performance WebSocket connection handling with a simple decorator API.
"""

import asyncio
from typing import Any, Callable, Optional


class WebSocket:
    """
    WebSocket connection wrapper.

    Provides methods for sending messages and iterating over received messages.
    """

    def __init__(self, connection):
        """
        Initialize WebSocket wrapper.

        Args:
            connection: Rust WebSocketConnection instance
        """
        self._connection = connection
        self._messages = asyncio.Queue()
        self._closed = False

    @property
    def id(self) -> int:
        """Get the unique session ID."""
        return self._connection.id

    async def send(self, message: str) -> None:
        """
        Send a text message to the client.

        Args:
            message: Text message to send
        """
        self._connection.send(message)

    async def send_binary(self, data: bytes) -> None:
        """
        Send binary data to the client.

        Args:
            data: Binary data to send
        """
        self._connection.send_binary(list(data))

    async def close(self, reason: Optional[str] = None) -> None:
        """
        Close the WebSocket connection.

        Args:
            reason: Optional close reason
        """
        self._closed = True
        self._connection.close(reason)

    def _receive_message(self, message: str) -> None:
        """Internal: Queue a received message."""
        self._messages.put_nowait(message)

    def _receive_close(self) -> None:
        """Internal: Mark connection as closed."""
        self._closed = True
        self._messages.put_nowait(None)

    async def receive(self) -> Optional[str]:
        """
        Receive the next message.

        Returns:
            The received message, or None if connection closed.
        """
        if self._closed:
            return None
        msg = await self._messages.get()
        return msg

    def __aiter__(self):
        """Async iterator protocol."""
        return self

    async def __anext__(self) -> str:
        """Get next message or raise StopAsyncIteration."""
        msg = await self.receive()
        if msg is None:
            raise StopAsyncIteration
        return msg


class WebSocketHandler:
    """
    Handler class for WebSocket connections.

    Used internally to bridge Python handlers with Rust WebSocket sessions.
    """

    def __init__(self, handler_func: Callable):
        """
        Initialize handler.

        Args:
            handler_func: Async function to handle WebSocket connections
        """
        self.handler_func = handler_func
        self._connections: dict[int, WebSocket] = {}

    def on_connect(self, session_id: int) -> None:
        """Called when a client connects."""
        # Connection setup happens in on_message for first message
        pass

    def on_message(self, session_id: int, message: str) -> Optional[str]:
        """Called when a text message is received. Returns response to send back."""
        # Simple echo implementation - just return the message with prefix
        # For production, this should integrate with the async handler properly
        return f"Echo: {message}"

    def on_binary(self, session_id: int, data: bytes) -> None:
        """Called when binary data is received."""
        # Binary messages can be handled similarly
        pass

    def on_disconnect(self, session_id: int, reason: Optional[str] = None) -> None:
        """Called when a client disconnects."""
        if session_id in self._connections:
            ws = self._connections[session_id]
            ws._receive_close()
            del self._connections[session_id]

    def register_connection(self, session_id: int, ws: WebSocket) -> None:
        """Register a new connection."""
        self._connections[session_id] = ws


def websocket_route(path: str):
    """
    Decorator for WebSocket route handlers.

    Usage:
        @app.websocket("/ws")
        async def ws_handler(ws):
            await ws.send("Welcome!")
            async for msg in ws:
                await ws.send(f"Echo: {msg}")

    Args:
        path: URL path for the WebSocket endpoint

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        func._websocket_path = path
        return func

    return decorator
