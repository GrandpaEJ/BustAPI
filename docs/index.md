# BustAPI

**The speed of Rust. The simplicity of Flask.**

<div align="center">
  <img src="assets/logo.png" alt="BustAPI Logo" width="200">
</div>

---

## 🚀 v0.8.0 Highlights

| Feature | Performance |
|:--------|------------:|
| **Multiprocessing** | 100,000+ RPS (Linux) |
| **Turbo Routes** | 30,000+ RPS |
| **Cached Routes** | 140,000+ RPS |
| **Cross-Platform** | Linux, macOS, Windows |

```python
from bustapi import BustAPI

app = BustAPI()

@app.turbo_route("/", cache_ttl=60)
def hello():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, workers=4)
```

---

## Features

- **Rust-Powered Performance**: Built on **Actix-web** via PyO3. Handles 100,000+ requests/sec with 4 workers.
- **Native Multiprocessing**: `SO_REUSEPORT` kernel load balancing on Linux for true parallelism.
- **Turbo Routes**: Zero-overhead handlers with typed path parameters parsed in Rust.
- **Built-in Caching**: `cache_ttl` parameter for instant cached responses.
- **Cross-Platform**: Runs on Linux (max performance), macOS, and Windows.

## Developer Experience

```python
from bustapi import BustAPI
from bustapi.safe import Struct, String

class User(Struct):
    name: String
    email: String

app = BustAPI()

@app.turbo_route("/users/<int:id>")
def get_user(id: int):
    return {"id": id, "name": f"User {id}"}

@app.post("/users")
async def create_user(user: User):
    return {"message": f"Welcome, {user.name}!"}
```

## Getting Started

Check out the [Quickstart](quickstart.md) or dive into the [Core Concepts](user-guide/routing.md).

### Platform Recommendations

| Platform | Mode | Best For |
|:---------|:-----|:---------|
| 🐧 **Linux** | Multiprocessing | Production (100k+ RPS) |
| 🍎 macOS | Single-process | Development |
| 🪟 Windows | Single-process | Development |

> ⚠️ **Production Tip:** Deploy on Linux servers for maximum performance with `SO_REUSEPORT` load balancing.
