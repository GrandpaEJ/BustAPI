# BustAPI — High-Performance Python Web Framework 
# [New Location]=>**[RUSTxPY](https://github.com/RUSTxPY/BustAPI)**

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


> [!IMPORTANT]
> **Migration Notice:** This project has officially moved to the **[RUSTxPY](https://github.com/RUSTxPY/BustAPI)** organization for better community maintenance and long-term stability. Please update your bookmarks and remotes.


---

## Example
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

## 📦 Installation

```bash
pip install bustapi
```

**Supports:** Python 3.10 – 3.14 | Linux, macOS, Windows | x86_64 & ARM64

Pre-built wheels available — no Rust toolchain required!

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
