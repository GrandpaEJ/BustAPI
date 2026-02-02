import asyncio
from typing import Set

from bustapi import BustAPI, WebSocketConfig

app = BustAPI()

# -------------------------------------------------------------------------
# 1. Configuration (Limits)
# -------------------------------------------------------------------------
# Protect your server from abuse
secure_config = WebSocketConfig(
    max_message_size=1024 * 4,  # 4 KB Limit
    rate_limit=20,  # 20 msgs/sec
    heartbeat_interval=15,  # Ping every 15s
    timeout=60,  # Timeout after 60s silence
)


# -------------------------------------------------------------------------
# 2. Standard WebSocket (Echo)
# -------------------------------------------------------------------------
@app.websocket("/ws/echo", config=secure_config)
async def echo_handler(ws):
    """Simple Echo Server"""
    print("Echo connected")
    try:
        async for msg in ws:
            await ws.send(f"You said: {msg}")
    except Exception as e:
        print(f"Echo error: {e}")
    finally:
        print("Echo disconnected")


# -------------------------------------------------------------------------
# 3. Chat Server (Broadcast)
# -------------------------------------------------------------------------
# Store active connections
active_connections: Set = set()


@app.websocket("/ws/chat")
async def chat_handler(ws):
    """Multi-user Chat"""
    active_connections.add(ws)
    print(f"Chat connected. Total: {len(active_connections)}")

    try:
        # Announce join
        for connection in active_connections:
            if connection != ws:
                await connection.send("A new user joined the chat!")

        async for msg in ws:
            # Broadcast to everyone else
            for connection in active_connections:
                if connection != ws:
                    await connection.send(f"User: {msg}")

    except Exception as e:
        print(f"Chat error: {e}")
    finally:
        active_connections.remove(ws)
        print(f"Chat disconnected. Total: {len(active_connections)}")


# -------------------------------------------------------------------------
# 4. Turbo WebSocket (High Performance)
# -------------------------------------------------------------------------
@app.websocket(
    "/ws/turbo", config=secure_config
)  # Note: Turbo actually uses @app.turbo_websocket
@app.turbo_websocket(
    "/ws/turbo_fast", response_prefix="FastEcho: ", config=secure_config
)
def turbo_handler():
    """
    Pure Rust Handler.
    Python function body is ignored.
    Handles 100k+ RPS.
    """
    pass


# -------------------------------------------------------------------------
# serve
# -------------------------------------------------------------------------
if __name__ == "__main__":
    print("🚀 WebSocket Demo Running on http://127.0.0.1:8000")
    print("Endpoins:")
    print(" - /ws/echo        (Standard Echo)")
    print(" - /ws/chat        (Broadcast Chat)")
    print(" - /ws/turbo_fast  (Turbo Rust Echo)")
    app.run(port=8000)
