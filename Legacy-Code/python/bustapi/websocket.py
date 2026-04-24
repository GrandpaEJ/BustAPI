"""
WebSocket support for BustAPI.

Provides high-performance WebSocket connection handling with a simple decorator API.
"""

import asyncio
import sys
from typing import Any, Callable, Dict, Optional, Tuple

from .bustapi_core import WebSocketConnection  # Import Rust class


class WebSocket:
    """
    WebSocket connection wrapper.

    Provides methods for sending messages and iterating over received messages.
    """

    def __init__(
        self,
        connection: WebSocketConnection,
        headers: Dict[str, str],
        cookies: Dict[str, str],
    ):
        """
        Initialize WebSocket wrapper.

        Args:
            connection: Rust WebSocketConnection instance
            headers: Request headers
            cookies: Request cookies
        """
        self._connection = connection
        self.headers = headers
        self.cookies = cookies
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

    def _receive_close(self, reason: Optional[str] = None) -> None:
        """Internal: Mark connection as closed."""
        self._closed = True
        self._messages.put_nowait(None)

    async def receive(self) -> Optional[str]:
        """
        Receive the next message.

        Returns:
            The received message, or None if connection closed.
        """
        if self._closed and self._messages.empty():
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
        self._connections: Dict[int, WebSocket] = {}
        self._tasks: Dict[int, asyncio.Task] = {}

    def on_connect(
        self, connection: Any, headers: Dict[str, str], cookies: Dict[str, str]
    ) -> None:
        """
        Called when a client connects.

        Args:
            connection: Rust PyWebSocketConnection object
            headers: Request headers dictionary
            cookies: Request cookies dictionary
        """
        print("[DEBUG] Python on_connect called for session", file=sys.stderr)
        # Create high-level WebSocket wrapper
        try:
            ws = WebSocket(connection, headers, cookies)
            # print(f"[DEBUG] WebSocket wrapper created: {ws.id}", file=sys.stderr)
        except Exception as e:
            print(f"[DEBUG] Error creating WebSocket wrapper: {e}", file=sys.stderr)
            return

        # Store connection
        self._connections[ws.id] = ws

        # Spawn the user's async handler
        try:
            loop = asyncio.get_running_loop()
            # print("[DEBUG] Using existing running loop", file=sys.stderr)
            task = loop.create_task(self.handler_func(ws))
        except RuntimeError:
            # We are likely in an Actix thread with no asyncio loop.
            # We must use a dedicated background loop for handlers.
            if not hasattr(self, "_background_loop") or self._background_loop is None:
                # Check for global existing loop?
                # Better: Lazy init a class-level or instance-level loop in a thread
                import threading

                def run_loop(loop_instance):
                    asyncio.set_event_loop(loop_instance)
                    loop_instance.run_forever()

                # print("[DEBUG] Starting background asyncio loop thread", file=sys.stderr)
                self._background_loop = asyncio.new_event_loop()
                t = threading.Thread(
                    target=run_loop, args=(self._background_loop,), daemon=True
                )
                t.start()

            loop = self._background_loop
            # print("[DEBUG] dispatching to background loop", file=sys.stderr)
            future = asyncio.run_coroutine_threadsafe(self.handler_func(ws), loop)
            # Wrapper to handle done callback since future is concurrent.futures.Future
            # We need to track it manually or map it
            self._tasks[ws.id] = future
            return  # run_coroutine_threadsafe returns a future, not a task we can add_done_callback easily in same way?
            # actually we can add_done_callback to the concurrent future.

        self._tasks[ws.id] = task

        # Add done callback to cleanup task and log errors
        def _task_done_callback(t):
            try:
                t.result()
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(
                    f"[ERROR] WebSocket handler task failed for session {ws.id}: {e}",
                    file=sys.stderr,
                )
            self._cleanup_task(ws.id)

        # Handle both Task (asyncio) and Future (threadsafe)
        if hasattr(task, "add_done_callback"):
            task.add_done_callback(_task_done_callback)

    def on_message(self, session_id: int, message: str) -> None:
        """Called when a text message is received."""
        if session_id in self._connections:
            ws = self._connections[session_id]
            # Since we might be running in a different thread (Actix thread)
            # than the WebSocket's loop (Background thread), we must use thread-safe scheduling.
            # We need to find the loop associated with this WebSocket's handler.
            loop = None
            if hasattr(self, "_background_loop") and self._background_loop:
                loop = self._background_loop
            else:
                # Fallback: try to get loop from registered task?
                pass

            if loop:
                loop.call_soon_threadsafe(ws._receive_message, message)
            else:
                # If no specific background loop, imply we are reusing the main loop?
                # But if we are in Actix thread, main loop might be running in main thread.
                # call_soon_threadsafe is safe to call from any thread to target loop.
                # However, if we don't have 'loop' var ...
                # ws._messages is bound to a loop. We should get it.
                # asyncio.Queue doesn't expose public ._loop, but we can try to guess.
                # Actually, check self._tasks[session_id].get_loop() if available py3.7+
                task = self._tasks.get(session_id)
                if task:
                    try:
                        loop = task.get_loop()
                        loop.call_soon_threadsafe(ws._receive_message, message)
                        return
                    except:
                        pass

                # Fallback to direct call if we can't find loop (risk of race)
                ws._receive_message(message)

        return None

    def on_binary(self, session_id: int, data: bytes) -> None:
        """Called when binary data is received."""
        if session_id in self._connections:
            ws = self._connections[session_id]
            # Convert if necessary, but data should come as bytes/list from bindings
            # If bindings use Vec<u8> -> list[int] in Python usually?
            # Or bytes?
            # Let's assume bytes for now or cast.
            if isinstance(data, list):
                data = bytes(data)
            ws._receive_message(data)

    def on_disconnect(self, session_id: int, reason: Optional[str] = None) -> None:
        """Called when a client disconnects."""
        if session_id in self._connections:
            ws = self._connections[session_id]
            ws._receive_close(reason)
            del self._connections[session_id]

        self._cleanup_task(session_id)

    def _cleanup_task(self, session_id: int):
        """Internal cleanup when handler task finishes."""
        if session_id in self._tasks:
            # We don't cancel here because this is called when task is DONE.
            del self._tasks[session_id]

    def register_connection(self, session_id: int, ws: WebSocket) -> None:
        """Register a new connection."""
        self._connections[session_id] = ws
