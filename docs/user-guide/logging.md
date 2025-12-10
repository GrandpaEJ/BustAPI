# Logging

BustAPI features a high-performance, colorful logging system implemented in Rust.

## Default Logger

By default, BustAPI logs every request with method, path, status, and duration (in microseconds or milliseconds).

```
[BustAPI] 2025-12-10 12:00:00 | 200 OK |  120µs | GET /api/status
```

## Using the Application Logger

You can access the logger in your application code.

```python
import logging

@app.route("/")
def index():
    app.logger.info("Index page accessed")
    return "Hello"
```

## Rust vs Python Logging

- **Rust Logger**: Handles request/response logs. It runs outside the GIL for maximum speed and does not block Python execution.
- **Python Logger**: Standard `logging` module for your application logic. BustAPI bridges these so you can see all logs in one stream.
