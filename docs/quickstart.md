# Quickstart

This guide will get you up and running with BustAPI in under 5 minutes.

## Minimal Application

A minimal BustAPI application looks a lot like a Flask app:

```python title="app.py"
from bustapi import BustAPI

app = BustAPI()

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/json")
def data():
    return {"status": "ok", "framework": "BustAPI"}

if __name__ == "__main__":
    app.run(debug=True)
```

## Running the Application

Save the file as `app.py` and run it with your Python interpreter:

```bash
python app.py
```

You will see the BustAPI startup banner:

```
┌───────────────────────────────────────────────────┐
│                   BustAPI v0.3.0                  │
│               http://127.0.0.1:5000               │
│       (bound on host 127.0.0.1 and port 5000)     │
│                                                   │
│ Handlers ............. 2   Processes ........... 16 │
│ Prefork ....... Disabled  PID ............. 1234  │
└───────────────────────────────────────────────────┘
```

Open your browser and navigate to:

- http://127.0.0.1:5000/ -> You see `Hello, World!`
- http://127.0.0.1:5000/json -> You see `{"status": "ok", "framework": "BustAPI"}`

## Explanation

1.  **`from bustapi import BustAPI`**: Imports the main `BustAPI` application class.
2.  **`app = BustAPI()`**: Creates an instance of the app. This initializes the underlying Rust server.
3.  **`@app.route("/")`**: Decorator to register a function as a route handler. By default, it handles `GET` requests.
4.  **`return "..."`**: Returning a string automatically creates a `text/html` response.
5.  **`return {...}`**: Returning a dictionary automatically creates a `application/json` response.
6.  **`app.run(debug=True)`**: Starts the development server. `debug=True` provides detailed error pages and enables **hot reloading** (server restarts automatically on code changes).

## Next Steps

Now that you have a running app, check out the **[User Guide](../user-guide/routing.md)** to learn about dynamic routing, request handling, and more.
