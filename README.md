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

For maximum performance, use `@app.turbo_route()`. Path parameters are parsed in Rust for zero Python overhead:

```python
# Static route
@app.turbo_route("/health")
def health():
    return {"status": "ok"}

# Dynamic route with typed params
@app.turbo_route("/users/<int:id>")
def get_user(id: int):
    return {"id": id, "name": f"User {id}"}

# Multiple parameters
@app.turbo_route("/posts/<int:pid>/comments/<int:cid>")
def get_comment(pid: int, cid: int):
    return {"post": pid, "comment": cid}
```

Supports `int`, `float`, `str`, and `path` parameter types.

> ⚠️ **Note:** Turbo routes skip middleware, sessions, and request context for speed. Use `@app.route()` if you need those features.

---
## Benchmarks 

```python
@app.route()
```

| Run         | Requests/sec  |
| :---------- | :------------ |
| Run 1       | 29,548.52     |
| Run 2       | 22,752.84     |
| Run 3       | 24,053.13     |
| Run 4       | 23,588.68     |
| Run 5       | 24,299.84     |
| **Average** | **24,848.60** |
| **Peak**    | **29,548.52** |


## Benchmarks Turbo

```python
@app.turbo_route()
```

<strong><b> Last benchmark </b></strong>
<p align="center">
  <img src="benchmarks/rps_comparison.png" alt="BustAPI vs Other Frameworks" width="700">
</p>

### Cross-Platform Performance (v0.8.0)

| Platform | RPS (Root) | RPS (JSON) | Mode |
|:---------|----------:|----------:|:-----|
| **Linux** | **105,012** | **99,142** | Multiprocessing (SO_REUSEPORT) |
| macOS | 35,560 | 27532 | Single-process |
| Windows | 17,772 | 17,844 | Single-process |



> 💡 **Maximum Performance:** Use `@app.turbo_route()` with `cache_ttl` for **~140,000 RPS** on cached endpoints!


---

## Platform Support

### 🐧 Linux (Recommended for Production)

Linux provides the **best performance** with native multiprocessing via `SO_REUSEPORT`:
- **100,000+ RPS** with 4 workers
- Kernel-level load balancing across processes
- Optimal for production deployments

```bash
# Production deployment on Linux
python app.py  # Automatically uses multiprocessing
```

### 🍎 macOS (Development)

Fully supported for development. Single-process mode (~35k RPS):
```bash
pip install bustapi
python app.py
```

### 🪟 Windows (Development)

Fully supported for development. Single-process mode (~17k RPS):
```bash
pip install bustapi
python app.py
```

> ⚠️ **Production Recommendation:** For maximum performance, deploy on **Linux servers**. macOS and Windows are ideal for development but lack the multiprocessing optimizations available on Linux.

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

## 💰 Support the Project

If you find BustAPI useful, consider supporting its development:

**Binance ID:** ```1010167458```

---

## 🌠 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=GrandpaEJ/BustAPI&type=Date)](https://www.star-history.com/#GrandpaEJ/BustAPI&Date)

---


## License

[MIT](LICENSE) © 2025 <strong>[GrandpaEJ](https://github.com/GrandpaEJ)</strong>

