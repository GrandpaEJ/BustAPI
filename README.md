# BustAPI — High-Performance Python Web Framework

<p align="center">
  <img src="https://github.com/GrandpaEJ/BustAPI/releases/download/v0.1.5/BustAPI.png" alt="BustAPI - Fast Python Web Framework powered by Rust and Actix-Web" width="200">
</p>

<p align="center">
  <strong>The fastest Python web framework for building REST APIs</strong><br>
  <em>Flask-like syntax • Rust-powered performance • Up to 20,000+ requests/sec</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/bustapi/"><img src="https://img.shields.io/pypi/v/bustapi?color=blue&style=for-the-badge&logo=pypi" alt="BustAPI on PyPI"></a>
  <a href="https://github.com/GrandpaEJ/BustAPI/actions"><img src="https://img.shields.io/github/actions/workflow/status/GrandpaEJ/BustAPI/ci.yml?style=for-the-badge&logo=github" alt="CI Status"></a>
  <a href="https://pypi.org/project/bustapi/"><img src="https://img.shields.io/pypi/pyversions/bustapi?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10 3.11 3.12 3.13 3.14"></a>
  <a href="https://github.com/GrandpaEJ/BustAPI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/GrandpaEJ/BustAPI?style=for-the-badge" alt="MIT License"></a>
</p>

---

## ⚡ What is BustAPI?

BustAPI is a **production-ready Python web framework** that combines the best of both worlds: **Python's simplicity** and **Rust's raw performance**.

Under the hood, BustAPI runs on [Actix-Web](https://actix.rs/) — consistently ranked among the fastest web frameworks across all programming languages. But you never touch Rust. You write clean, familiar Python code with Flask-style decorators.

### Why BustAPI?

| Problem | BustAPI Solution |
|---------|------------------|
| Python web frameworks are slow | Rust core handles HTTP, JSON, routing |
| ASGI/WSGI adds overhead | Built-in server, no middleware layers |
| Scaling requires complex setup | Native multiprocessing with `SO_REUSEPORT` |
| Auth is always a pain | JWT, sessions, Argon2 hashing built-in |

### Key Highlights

- 🚀 **20,000+ RPS** out of the box — 5x faster than Flask
- 🦀 **Rust-powered** — Zero-copy JSON, mimalloc allocator, Actix-Web
- 🐍 **Pure Python API** — No Rust knowledge required
- 🔒 **Security built-in** — JWT, sessions, CSRF, rate limiting
- 📦 **Zero config** — `pip install bustapi` and you're ready
- 🔥 **Hot reload** — Rust-native file watcher for instant restarts

```python
from bustapi import BustAPI

app = BustAPI()

@app.route("/")
def hello():
    return {"message": "Hello, world!"}

if __name__ == "__main__":
    app.run()
```

No ASGI servers needed. No complex configuration. Just run your file.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Python Code                        │
│              (Flask-like decorators & handlers)             │
├─────────────────────────────────────────────────────────────┤
│                    PyO3 Bindings (v0.27)                    │
│              (Zero-cost Python ↔ Rust bridge)               │
├─────────────────────────────────────────────────────────────┤
│                  Rust Core (bustapi_core)                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │ Actix-Web   │ │ serde_json  │ │ mimalloc allocator      ││
│  │ HTTP Server │ │ Zero-copy   │ │ Optimized memory        ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

| Component | Technology | Purpose |
|-----------|------------|---------|
| HTTP Server | Actix-Web 4.x | Ultra-fast async HTTP handling |
| Serialization | serde_json | Zero-copy JSON encoding |
| Memory | mimalloc | High-performance allocator |
| Bindings | PyO3 0.27 | Python 3.10–3.14 support |
| Async Runtime | Tokio | Non-blocking I/O |

---

## 📦 Installation

```bash
pip install bustapi
```

**Supports:** Python 3.10 – 3.14 | Linux, macOS, Windows | x86_64 & ARM64

Pre-built wheels available — no Rust toolchain required!

---

## ✨ Features

### 🛣️ Routing
- **Dynamic Routes** — `/users/<int:id>` with automatic type validation
- **Blueprints** — Modular app organization (Flask-style)
- **Turbo Routes** — Zero-overhead handlers for maximum speed
- **Wildcard Paths** — `<path:filepath>` for catch-all routes

### 🔐 Authentication & Security
- **JWT** — Create/validate tokens (HS256, HS384, HS512)
- **Sessions** — Flask-Login compatible user management
- **Password Hashing** — Argon2id (OWASP recommended)
- **CSRF Protection** — Built-in token validation
- **Rate Limiting** — Rust-powered request throttling

### 🌐 HTTP Features
- **WebSocket** — Full duplex communication + Turbo mode
- **Streaming** — HTTP Range requests, video seeking
- **File Uploads** — Multipart form handling
- **Static Files** — Efficient serving with caching

### 🛠️ Developer Experience
- **Hot Reload** — Rust-native file watcher (instant restarts)
- **Templates** — Built-in Jinja2 via MiniJinja
- **CLI Tool** — `bustapi new`, `bustapi run`, `bustapi routes`
- **Auto-docs** — OpenAPI/Swagger generation
- **Testing** — Built-in `TestClient` for unit tests

### 🔌 Compatibility
- **ASGI/WSGI** — Works with Uvicorn, Gunicorn, Hypercorn
- **FastAPI-style** — `Query()`, `Path()`, `Body()`, `Depends()`
- **Flask-style** — `request`, `session`, `g`, `current_app`

---

## 🚀 Quick Start

**1. Create `app.py`:**

```python
from bustapi import BustAPI, jsonify

app = BustAPI()

@app.route("/")
def home():
    return {"status": "running", "framework": "BustAPI"}

@app.route("/users/<int:user_id>")
def get_user(user_id):
    return jsonify({"id": user_id, "name": "Alice"})

@app.route("/greet", methods=["POST"])
def greet():
    from bustapi import request
    data = request.json
    return {"message": f"Hello, {data.get('name', 'World')}!"}

if __name__ == "__main__":
    app.run(debug=True)  # Hot reload enabled
```

**2. Run it:**

```bash
python app.py
```

**3. Visit** `http://127.0.0.1:5000`

---

## ⚡ Turbo Routes

For **maximum performance**, use `@app.turbo_route()`. Path parameters are parsed entirely in Rust:

```python
# Zero-overhead static route
@app.turbo_route("/health")
def health():
    return {"status": "ok"}

# Dynamic route with typed params (parsed in Rust)
@app.turbo_route("/users/<int:id>")
def get_user(id: int):
    return {"id": id, "name": f"User {id}"}

# Cached response (140k+ RPS!)
@app.turbo_route("/config", cache_ttl=60)
def get_config():
    return {"version": "1.0", "env": "production"}
```

**Supported types:** `int`, `float`, `str`, `path`

> ⚠️ **Note:** Turbo routes skip middleware, sessions, and request context for speed. Use `@app.route()` when you need those features.

---

## 📊 Benchmarks

### Standard Routes (`@app.route()`)

| Platform | RPS | Mode |
|----------|----:|------|
| **Linux** | **~25,000** | Single-process |
| macOS | ~20,000 | Single-process |
| Windows | ~17,000 | Single-process |

### Turbo Routes (`@app.turbo_route()`) — Linux

| Configuration | RPS |
|---------------|----:|
| Static route | ~30,000 (single) |
| **Multiprocessing (4 workers)** | **~105,000** |
| **Cached (60s TTL)** | **~140,000** |

### Framework Comparison (Turbo + Multiprocessing)

<p align="center">
  <img src="benchmarks/rps_comparison.png" alt="BustAPI vs Other Frameworks" width="700">
</p>

---

## 🌍 Platform Support

### 🐧 Linux (Recommended for Production)

Linux delivers the **best performance** with native multiprocessing:

- **~25k RPS** standard routes, **100k+ RPS** with Turbo + multiprocessing
- Kernel-level load balancing via `SO_REUSEPORT`
- Automatic worker scaling to CPU cores

```bash
python app.py  # Automatically uses multiprocessing
```

### 🍎 macOS (Development)

Fully supported for development. Single-process mode (~35k RPS):

```bash
pip install bustapi && python app.py
```

### 🪟 Windows (Development)

Fully supported for development. Single-process mode (~17k RPS):

```bash
pip install bustapi && python app.py
```

> 💡 **Tip:** For production, deploy on **Linux servers** to unlock multiprocessing performance.

---

## 🔐 Authentication

### JWT Tokens

```python
from bustapi import BustAPI
from bustapi.jwt import JWT

app = BustAPI()
jwt = JWT(app, secret_key="your-secret-key")

@app.route("/login", methods=["POST"])
def login():
    # Validate credentials...
    token = jwt.create_access_token(identity=user_id)
    return {"access_token": token}

@app.route("/protected")
@jwt.jwt_required()
def protected():
    return {"user": jwt.get_jwt_identity()}
```

### Session Login

```python
from bustapi.auth import LoginManager, login_user, current_user, login_required

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/login", methods=["POST"])
def login():
    user = authenticate(request.form)
    login_user(user)
    return redirect("/dashboard")

@app.route("/dashboard")
@login_required
def dashboard():
    return f"Welcome, {current_user.name}!"
```

### Password Hashing

```python
from bustapi.auth import hash_password, verify_password

# Hash (Argon2id)
hashed = hash_password("mysecretpassword")

# Verify
if verify_password("mysecretpassword", hashed):
    print("Password correct!")
```

---

## 🌐 WebSocket

```python
@app.websocket("/ws")
async def websocket_handler(ws):
    await ws.accept()
    while True:
        message = await ws.receive_text()
        await ws.send_text(f"Echo: {message}")
```

**Turbo WebSocket** (Pure Rust, ~74% faster):

```python
@app.turbo_websocket("/ws/turbo")
def turbo_handler(message: str) -> str:
    return f"Echo: {message}"  # Processed entirely in Rust
```

---

## 🧪 Testing

```python
from bustapi.testing import TestClient

def test_homepage():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "running"}

def test_create_user():
    response = client.post("/users", json={"name": "Alice"})
    assert response.status_code == 201
```

---

## 📁 Project Structure

```
bustapi/
├── src/                    # Rust core
│   ├── lib.rs              # PyO3 module entry
│   ├── bindings/           # Python ↔ Rust bridge
│   ├── router/             # URL matching engine
│   ├── server/             # Actix-Web handlers
│   ├── websocket/          # WS session management
│   ├── jwt.rs              # Token encoding/decoding
│   └── crypto.rs           # Argon2, CSRF, tokens
│
├── python/bustapi/         # Python package
│   ├── app.py              # BustAPI main class
│   ├── auth/               # JWT, sessions, CSRF
│   ├── routing/            # Blueprints, decorators
│   ├── params.py           # Query/Path/Body validators
│   └── websocket.py        # WebSocket API
│
├── examples/               # 30+ usage examples
├── tests/                  # Comprehensive test suite
├── docs/                   # MkDocs documentation
└── benchmarks/             # Performance tools
```

---

## 🛠️ CLI Tool

```bash
# Create new project
bustapi new myproject

# Run with hot reload
bustapi run

# List all routes
bustapi routes

# Show system info
bustapi info
```

---

## 🚢 Deployment

### Built-in Server (Recommended)

```bash
python app.py
```

Uses the internal Rust HTTP server. Best performance, zero dependencies.

### With ASGI (Uvicorn)

```bash
pip install uvicorn
uvicorn app:app.asgi_app --host 0.0.0.0 --port 8000
```

### With Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

---

## 📖 Documentation

📚 **[Full Documentation](https://grandpaej.github.io/BustAPI/)**

- [Getting Started](https://grandpaej.github.io/BustAPI/quickstart/)
- [Routing Guide](https://grandpaej.github.io/BustAPI/user-guide/routing/)
- [JWT Authentication](https://grandpaej.github.io/BustAPI/user-guide/jwt/)
- [WebSocket Guide](https://grandpaej.github.io/BustAPI/user-guide/websocket/)
- [API Reference](https://grandpaej.github.io/BustAPI/api-reference/)

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing`)
5. **Open** a Pull Request

Found a bug? Have a feature request?

- [Open an Issue](https://github.com/GrandpaEJ/bustapi/issues)
- [Start a Discussion](https://github.com/GrandpaEJ/bustapi/discussions)

---

## 💰 Support

If BustAPI helps your project, consider supporting its development:

**Binance ID:** `1010167458`

---

## 🌠 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=GrandpaEJ/BustAPI&type=Date)](https://www.star-history.com/#GrandpaEJ/BustAPI&Date)

---

## 📄 License

[MIT](LICENSE) © 2025-2026 **[GrandpaEJ](https://github.com/GrandpaEJ)**

---

<p align="center">
  <strong>Built with 🦀 Rust + 🐍 Python</strong><br>
  <em>Fast. Simple. Production-ready.</em>
</p>
