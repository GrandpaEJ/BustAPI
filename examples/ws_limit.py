import asyncio

from bustapi import BustAPI, WebSocketConfig

app = BustAPI()

# Limit: 5 messages/sec, Max 100 bytes payload
config = WebSocketConfig(
    max_message_size=100,  # 100 Bytes limit (RAM protection)
    rate_limit=5,  # 5 msgs/sec limit (CPU protection)
)


@app.websocket("/ws", config=config)
async def echo_limited(ws):
    print("New connection")
    async for msg in ws:
        await ws.send(f"Echo: {msg}")


@app.turbo_websocket("/ws/turbo", config=config)
def turbo_echo():
    pass


if __name__ == "__main__":
    print("Running WebSocket Limit Demo on port 8080")
    print("Limits: Max 100 bytes, 5 msgs/sec")
    app.run(port=8080)
