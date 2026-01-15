# BustAPI

<div align="center" markdown>

![BustAPI Logo](assets/logo.png){ width="150" }

**High-performance Python web framework with Rust backend**

[:material-rocket-launch: Get Started](quickstart.md){ .md-button .md-button--primary }
[:material-github: GitHub](https://github.com/GrandpaEJ/BustAPI){ .md-button }

</div>

---

## What is BustAPI?

BustAPI is a **Flask-compatible** Python web framework powered by [Actix-web](https://actix.rs/) (Rust). You write normal Python code, and BustAPI handles requests with Rust-level performance.

```python
from bustapi import BustAPI

app = BustAPI()

@app.route("/")
def hello():
    return {"message": "Hello, World!"}

@app.route("/users/<int:id>")
def get_user(id: int):
    return {"id": id, "name": f"User {id}"}

if __name__ == "__main__":
    app.run(debug=True)
```

---

## Features

- **Flask-like API** - Familiar decorators: `@app.route()`, `@app.get()`, `@app.post()`
- **Rust Performance** - Fast HTTP parsing via Actix-web
- **Turbo Routes** - `@app.turbo_route()` for high-throughput endpoints
- **Multiprocessing** - `workers=4` for parallel request handling on Linux
- **JWT Authentication** - Built-in token-based auth
- **Templates** - Jinja2 template rendering
- **Blueprints** - Modular app organization

---

## Performance

Benchmarked with `wrk -t4 -c50 -d10s` on Python 3.13, Intel i5 (4 cores):

| Endpoint | Linux (4 workers) | macOS | Windows |
|:---------|------------------:|------:|--------:|
| `/` (turbo) | 105,012 RPS | 35,560 RPS | 17,772 RPS |
| `/json` (turbo) | 99,142 RPS | 27,532 RPS | 17,844 RPS |

!!! tip "Best Performance"
    Use Linux for production to enable `SO_REUSEPORT` multiprocessing.

---

## Installation

```bash
pip install bustapi
```

Supports Python **3.10 - 3.14** on Linux, macOS, and Windows.

---

## Next Steps

- [Quickstart Guide](quickstart.md) - Build your first app
- [Routing Guide](user-guide/routing.md) - Dynamic paths and methods
- [Turbo Routes](user-guide/turbo-routes.md) - Maximum performance
- [Multiprocessing](user-guide/multiprocessing.md) - Scale to 100k+ RPS
- [JWT Auth](user-guide/jwt.md) - Secure your API
