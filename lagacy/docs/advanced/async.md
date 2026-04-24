# Async Support

Python's `async/await` syntax allows for cooperative multitasking, which is ideal for I/O-bound web applications. BustAPI runs on an asynchronous event loop powered by Rust.

## Async Handlers

Defining an async handler is as simple as adding the `async` keyword.

```python
import asyncio

@app.route("/sleep")
async def sleep():
    await asyncio.sleep(1)
    return "Woke up!"
```

## When to use Async?

!!! tip "Use Async for:"
    - Database queries (using async drivers like `motor` or `asyncpg`).
    - Calling external APIs (using `httpx` or `aiohttp`).
    - File I/O.

!!! warning "Avoid specific blocking calls"
    Do not use blocking calls like `time.sleep()` or standard `requests.get()` inside an async route. This will block the entire event loop and freeze your server.

## Background Tasks

Sometimes you want to perform an action after returning a response, like sending an email. BustAPI provides `BackgroundTasks` for this.

```python
from bustapi import BackgroundTasks

def send_email(email: str, message: str):
    # Simulated email sending
    print(f"Sending email to {email}")

@app.post("/signup")
def signup(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_email, email, "Welcome!")
    return {"status": "User created, email scheduled"}
```

## Mixing Sync and Async

BustAPI is smart enough to handle both. Standard synchronous functions are run in a thread pool to avoid blocking the async event loop.
