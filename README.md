# BustAPI — High-Performance Python Web Framework

<p align="center">
  <img src="https://github.com/GrandpaEJ/BustAPI/releases/download/v0.1.5/BustAPI.png" alt="BustAPI - Fast Python Web Framework powered by Rust and Actix-Web" width="200">
</p>

<p align="center">
  <strong>The fastest Python web framework for building REST APIs</strong><br>
  <em>Flask-like syntax • Rust-powered performance • 20,000+ requests/sec</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/bustapi/"><img src="https://img.shields.io/pypi/v/bustapi?color=blue&style=for-the-badge&logo=pypi" alt="BustAPI on PyPI"></a>
  <a href="https://github.com/GrandpaEJ/BustAPI/actions"><img src="https://img.shields.io/github/actions/workflow/status/GrandpaEJ/BustAPI/ci.yml?style=for-the-badge&logo=github" alt="CI Status"></a>
  <a href="https://pypi.org/project/bustapi/"><img src="https://img.shields.io/pypi/pyversions/bustapi?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10 3.11 3.12 3.13 3.14"></a>
  <a href="https://github.com/GrandpaEJ/BustAPI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/GrandpaEJ/BustAPI?style=for-the-badge" alt="MIT License"></a>
</p>

---

## What is BustAPI?

BustAPI is a Python web framework that runs on a Rust core. You write normal Python code, but requests are handled by [Actix-Web](https://actix.rs/) under the hood.

The result? **Flask-like code that handles 20,000+ requests per second.**

```python
from bustapi import BustAPI

app = BustAPI()

@app.route("/")
def hello():
    return {"message": "Hello, world!"}

if __name__ == "__main__":
    app.run()
```

That's it. No ASGI servers, no special configuration. Just run your file.

---

## Installation

```bash
pip install bustapi
```

**Python 3.10 - 3.14** supported. Pre-built wheels available for Linux, macOS, and Windows.

---

## Features

### Core
- **Routing** — Dynamic paths like `/users/<int:id>` with type validation
- **Blueprints** — Organize large apps into modules
- **Templates** — Built-in Jinja2 support
- **Middleware** — `@app.before_request` and `@app.after_request` hooks
- **Hot Reload** — Automatic restart on file changes (Rust-native, no watchfiles needed)

### Authentication
- **JWT** — Create and validate tokens with HS256/384/512
- **Sessions** — Flask-Login style user management
- **Password Hashing** — Argon2id via Rust for secure password storage

### Performance
- **Native JSON** — Responses serialized in Rust with `serde_json`
- **Multiprocessing** — Fork workers with `SO_REUSEPORT` for true parallelism
- **Turbo Routes** — Zero-overhead handlers for simple endpoints

---

## Quick Start

Create `app.py`:

```python
from bustapi import BustAPI, jsonify

app = BustAPI()

@app.route("/")
def home():
    return {"status": "running"}

@app.route("/users/<int:user_id>")
def get_user(user_id):
    return jsonify({"id": user_id, "name": "Alice"})

if __name__ == "__main__":
    app.run(debug=True)  # Hot reload enabled
```

Run it:

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

---

## Turbo Routes

For maximum performance on simple endpoints, use `@app.turbo_route()`. It skips request context, sessions, and middleware for zero-overhead handling:

```python
@app.turbo_route("/health")
def health():
    return {"status": "ok"}

@app.turbo_route("/api/stats")
def stats():
    return {"users": 1000, "requests": 5000000}
```

Turbo routes are ideal for health checks, metrics, and high-frequency read endpoints.

> ⚠️ **Note:** Turbo routes currently only support static paths. Dynamic endpoints like `/users/<int:id>` are not yet supported—use regular `@app.route()` for those.

---

## Benchmarks

Tested on Python 3.13, Intel i5-8365U (8 cores), Ubuntu Linux:

| Framework | Requests/sec | Memory |
|:----------|-------------:|-------:|
| **BustAPI** | **18,500** | **45 MB** |
| Catzilla | 11,170 | 1,496 MB |
| Flask (4 workers) | 4,988 | 159 MB |
| FastAPI (4 workers) | 2,000 | 232 MB |

BustAPI achieves **9x higher throughput** than FastAPI with **5x less memory**.

> 💡 **Want more speed?** Use `@app.turbo_route()` for simple endpoints to hit **35k+ RPS**.

---

## Deployment

### Built-in Server (Recommended)

```bash
python app.py
```

Uses the internal Rust HTTP server. Best performance, zero dependencies.

### With ASGI (Uvicorn)

```bash
pip install uvicorn
uvicorn app:app.asgi_app --interface asgi3
```

### With WSGI (Gunicorn)

```bash
pip install gunicorn
gunicorn app:app
```

---

## Documentation

📖 **[Full Documentation](https://grandpaej.github.io/BustAPI/)**

- [Getting Started](https://grandpaej.github.io/BustAPI/quickstart/)
- [Routing Guide](https://grandpaej.github.io/BustAPI/user-guide/routing/)
- [JWT Authentication](https://grandpaej.github.io/BustAPI/user-guide/jwt/)
- [API Reference](https://grandpaej.github.io/BustAPI/api-reference/)

---

## Contributing

Found a bug? Have a feature request?

- [Open an Issue](https://github.com/GrandpaEJ/bustapi/issues)
- [Start a Discussion](https://github.com/GrandpaEJ/bustapi/discussions)

---

## License

[MIT](LICENSE) © 2025 GrandpaEJ
