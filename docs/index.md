# BustAPI

**The speed of Rust. The simplicity of Flask.**

`BustAPI` is a high-performance, async-native, type-safe Python web framework built on top of Rust bindings. It is designed to be a drop-in high-performance alternative to Flask-like frameworks.

<div align="center">
  <img src="assets/logo.png" alt="BustAPI Logo" width="200">
</div>

---

## Features

- **Rust-Powered Performance**: Built on top of **Actix-web** via PyO3 bindings. BustAPI handles the heavy lifting of HTTP parsing and routing in optimized Rust code, while your business logic stays in friendly Python.
- **Type-Safe by Design**: Leveraging Python's `typing` module, BustAPI enforces rigorous validation using Rust-based validators. Errors are caught early with descriptive messages.
- **True Async Support**: Designed for modern I/O-bound workloads. BustAPI runs on a dedicated Rust event loop, allowing you to handle thousands of concurrent connections efficiently.

## Developer Experience


```python
from bustapi import BustAPI, Body
from bustapi.safe import Struct, String

class User(Struct):
    name: String
    email: String

app = BustAPI()

@app.post("/users")
async def create_user(user: User = Body(...)):
    # user is strictly validated!
    return {"message": f"Welcome, {user.name}!"}
```

## Getting Started

Check out the [Quickstart](quickstart.md) or dive into the [Core Concepts](user-guide/routing.md).
