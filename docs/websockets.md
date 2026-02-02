
# WebSocket Support

BustAPI provides high-performance WebSocket support powered by Rust (Actix-Web). It offers two implementation strategies: **Standard** (flexible Python handling) and **Turbo** (zero-overhead Rust handling).

## Configuration & Limits

To protect your application from abuse (DDoS, OOM), you can configure limits using `WebSocketConfig`.

```python
from bustapi import BustAPI, WebSocketConfig

app = BustAPI()

# Define protection limits
config = WebSocketConfig(
    max_message_size=1024 * 64,  # 64 KB Max Message Size (RAM Protection)
    rate_limit=50,               # 50 Messages/Second (CPU Protection)
    heartbeat_interval=10,       # Send Ping every 10 seconds
    timeout=30                   # Disconnect if silence for 30 seconds
)
```

## 1. Standard WebSockets (`@app.websocket`)

Use this for complex logic where you need Python libraries (database access, AI models, complex parsing).

```python
@app.websocket("/ws/chat", config=config)
async def chat_handler(ws):
    # 'ws' acts as an async iterator
    async for message in ws:
        # Process in Python (Hit GIL)
        response = f"You said: {message}"
        await ws.send(response)
```

*   **Pros:** Full Python flexibility.
*   **Cons:** Limited by Python GIL (~5k-10k msgs/sec per core).

## 2. Turbo WebSockets (`@app.turbo_websocket`) 🚀

Use this for high-throughput scenarios like ECHO servers, broadcasting, or simple relays where Python processing isn't strictly necessary for every message.

```python
# Messages are handled entirely in Rust!
# Prefix: Prepended to every message automatically.
@app.turbo_websocket("/ws/echo", response_prefix="Echo: ", config=config)
def turbo_echo():
    pass 
```

*   **Pros:** Zero GIL overhead, 100k+ msgs/sec, ultra-low latency.
*   **Cons:** Logic is limited to predefined Rust handlers (currently Echo/Broadcast).

## Performance Comparison (Handshakes/sec)

BustAPI handles connections significantly faster than Python-native ASGI frameworks because the handshake upgrade happens in Rust threads.

| Framework | Implementation | Handshakes/sec | Efficiency |
| :--- | :--- | :--- | :--- |
| **BustAPI** | Rust + Python | **~12,000+** 🚀 | High |
| **Flask/Quart** | Python | ~400-500 | Low |
| **FastAPI** | Python (ASGI) | ~250 | Low |

> **Note:** Enabling `rate_limit` in `WebSocketConfig` has negligible performance impact as it is enforced in Rust.

## Scaling Guide

*   **CPU:** Use `rate_limit` to prevent a single client from monopolizing the CPU.
*   **RAM:** Use `max_message_size` to prevent large payloads from crashing the server.
*   **Concurrency:** To handle >10k concurrent connections, ensure your OS file descriptor limits (`ulimit -n`) are raised.

## Complete Example

Check out the [comprehensive WebSocket demo](https://github.com/GrandpaEJ/BustAPI/blob/main/examples/websockets_demo.py) which includes:
*   Secure Configuration (Limits)
*   Standard Echo
*   Broadcast Chat
*   Turbo Routes

Run it locally:
```bash
python examples/websockets_demo.py
```
