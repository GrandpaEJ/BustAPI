import asyncio
import json
import os
import sys
from typing import Set

# Ensure we can import bustapi from local source if running from repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
# Also add python/ path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../python"))
)

from bustapi import BustAPI

app = BustAPI(template_folder="templates")


# Simple in-memory connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[any] = set()
        self.counter = 0

    async def connect(self, ws):
        self.counter += 1
        # ws.id is read-only (session ID from Rust), do not overwrite!
        # ws.id = self.counter
        ws.username = f"Guest {self.counter}"
        self.active_connections.add(ws)
        print(f"[Manager] User connected: {ws.username} (ID: {ws.id})")
        await self.broadcast(
            {"type": "system", "text": f"{ws.username} joined the chat."}
        )

    async def disconnect(self, ws):
        if ws in self.active_connections:
            self.active_connections.remove(ws)
            print(f"[Manager] User disconnected: {ws.username}")
            await self.broadcast(
                {"type": "system", "text": f"{ws.username} left the chat."}
            )

    async def broadcast(self, message: dict):
        # We need to serialize message.
        # For simplicity, we send JSON string.
        msg_json = json.dumps(message)

        # Iterate over copy to avoid modification issues if disconnect happens during send (unlikely but safe)
        for connection in list(self.active_connections):
            try:
                # If we want to distinguish "me" from "others" in the message efficiently,
                # we could customize the payload per user, but here we let the client handle logic
                # or just send generic info.

                # Let's augment message for "me" logic IF it's a user message
                if "sender_id" in message and message["sender_id"] == connection.id:
                    # Clone message for sender
                    my_msg = message.copy()
                    my_msg["is_me"] = True
                    my_msg["sender"] = "You"
                    await connection.send(json.dumps(my_msg))
                else:
                    # Regular message for others
                    await connection.send(msg_json)

            except Exception as e:
                print(f"[Manager] Error broadcasting to {connection.username}: {e}")
                # cleanup dead connection? The disconnect handler should handle this on next cycle or error
                pass


manager = ConnectionManager()


@app.route("/")
def index():
    return app.render_template("index.html")


@app.websocket("/chat")
async def chat_endpoint(ws):
    await manager.connect(ws)
    try:
        async for msg in ws:
            # Broadcast received message
            await manager.broadcast(
                {
                    "type": "message",
                    "text": msg,
                    "sender": ws.username,
                    "sender_id": ws.id,
                }
            )
    except Exception as e:
        print(f"[Handler] Error: {e}")
    finally:
        await manager.disconnect(ws)


if __name__ == "__main__":
    print("Starting AnonChat on http://localhost:5000")
    app.run(port=5000, debug=True)
