"""
BustAPI Turbo WebSocket Example

Demonstrates high-performance WebSocket handling with pure Rust processing.
No Python calls during message loop = maximum performance.

Compare with 28_websocket.py for the Full Python mode.
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
        <title>BustAPI Turbo WebSocket Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            #messages { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll; margin-bottom: 10px; }
            #input { width: 80%; padding: 10px; }
            button { padding: 10px 20px; }
            .sent { color: blue; }
            .received { color: green; }
            .system { color: gray; font-style: italic; }
            .turbo { background: linear-gradient(90deg, #ff6b6b, #feca57); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        </style>
    </head>
    <body>
        <h1>🚀 BustAPI <span class="turbo">TURBO</span> WebSocket Demo</h1>
        <p><strong>Pure Rust Message Processing - Maximum Performance!</strong></p>
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

            log('Connecting to Turbo WebSocket...');
            const ws = new WebSocket('ws://' + window.location.host + '/ws/turbo');

            ws.onopen = () => log('Connected! (TURBO MODE)');
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


# Turbo WebSocket - Pure Rust echo
@app.turbo_websocket("/ws/turbo")
def turbo_echo():
    """This function body is ignored - all processing happens in Rust!"""
    pass


if __name__ == "__main__":
    print("Turbo WebSocket server running on http://127.0.0.1:8006")
    print("Open in browser to test, or use: websocat ws://127.0.0.1:8006/ws/turbo")
    app.run(host="127.0.0.1", port=8006, debug=True)
