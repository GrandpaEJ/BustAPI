"""
BustAPI WebSocket Example

Demonstrates high-performance WebSocket handling with the @app.websocket() decorator.

Test with:
    websocat ws://127.0.0.1:8005/ws
    (or any WebSocket client)
"""

from bustapi import BustAPI

app = BustAPI()


@app.route("/")
def index():
    """Serve a simple HTML page with WebSocket client."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BustAPI WebSocket Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            #messages { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll; margin-bottom: 10px; }
            #input { width: 80%; padding: 10px; }
            button { padding: 10px 20px; }
            .sent { color: blue; }
            .received { color: green; }
            .system { color: gray; font-style: italic; }
        </style>
    </head>
    <body>
        <h1>🚀 BustAPI WebSocket Demo</h1>
        <div id="messages"></div>
        <input type="text" id="input" placeholder="Type a message..." onkeypress="if(event.keyCode==13) send()">
        <button onclick="send()">Send</button>

        <script>
            const messages = document.getElementById('messages');
            const input = document.getElementById('input');

            function log(msg, type='system') {
                const div = document.createElement('div');
                div.className = type;
                div.textContent = (type === 'sent' ? '→ ' : type === 'received' ? '← ' : '') + msg;
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            }

            log('Connecting to WebSocket...');
            const ws = new WebSocket('ws://' + window.location.host + '/ws');

            ws.onopen = () => log('Connected!');
            ws.onclose = () => log('Disconnected');
            ws.onerror = (e) => log('Error: ' + e);
            ws.onmessage = (e) => log(e.data, 'received');

            function send() {
                const msg = input.value.trim();
                if (msg && ws.readyState === WebSocket.OPEN) {
                    ws.send(msg);
                    log(msg, 'sent');
                    input.value = '';
                }
            }
        </script>
    </body>
    </html>
    """


@app.websocket("/ws")
async def ws_handler(ws):
    """
    WebSocket handler - echoes messages back to client.

    This handler is called when a client connects to /ws.
    The `ws` object provides methods for sending and receiving messages.
    """
    # Send welcome message
    await ws.send("Welcome to BustAPI WebSocket! Type a message and I'll echo it back.")

    # Echo loop - iterate over incoming messages
    async for message in ws:
        # Echo the message back with a prefix
        await ws.send(f"Echo: {message}")


if __name__ == "__main__":
    print("WebSocket server running on http://127.0.0.1:8005")
    print("Open in browser to test, or use: websocat ws://127.0.0.1:8005/ws")
    app.run(host="127.0.0.1", port=8005, debug=True)
