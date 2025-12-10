# Async Support

One of BustAPI's main advantages over Flask is its first-class support for `async/await`.

## Overview

Traditional WSGI frameworks (like Flask) are synchronous. If one request blocks (example: checking a database), the worker thread is blocked. BustAPI runs on an asynchronous Rust runtime, allowing it to handle thousands of concurrent connections efficiently.

## Using Async Routes

Simply define your route handler with `async def`.

```python
import asyncio

@app.route("/sleep")
async def sleep():
    # This does NOT block the server!
    await asyncio.sleep(1)
    return "Woke up!"
```

## Mixing Sync and Async

You can mix synchronous and asynchronous routes in the same application.

- **Sync routes**: Run efficiently in a dedicated thread pool to avoid blocking the async event loop.
- **Async routes**: Run directly on the event loop for maximum concurrency.

## Best Practices

1.  **Use async drivers**: When using databases (like Postgres or Redis), use async libraries (e.g., `asyncpg`, `motor`, `redis-py`) to get the full benefit.
2.  **Avoid blocking CPU**: Creating thumbnails or processing heavy data inside an `async def` function will block the loop. For these tasks, define a standard `def` function (sync), and BustAPI will automatically offload it to a thread.
