# 🚀 BustAPI

<p align="center">
  <img src="https://github.com/GrandpaEJ/BustAPI/releases/download/v0.1.5/BustAPI.png" alt="BustAPI Logo" width="250">
</p>

<p align="center">
  <strong>The Ultra-High Performance Python Web Framework</strong><br>
  <em>Powered by Rust. Designed for Python. Built for the Future.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/bustapi/"><img src="https://img.shields.io/pypi/v/bustapi?color=blue&style=for-the-badge&logo=pypi" alt="PyPI"></a>
  <a href="https://github.com/GrandpaEJ/BustAPI/actions"><img src="https://img.shields.io/github/actions/workflow/status/GrandpaEJ/BustAPI/ci.yml?style=for-the-badge&logo=github" alt="CI"></a>
  <a href="https://pypi.org/project/bustapi/"><img src="https://img.shields.io/pypi/pyversions/bustapi?style=for-the-badge&logo=python&logoColor=white" alt="Versions"></a>
  <a href="https://github.com/GrandpaEJ/BustAPI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/GrandpaEJ/BustAPI?style=for-the-badge" alt="License"></a>
</p>

---

## ⚡ What is BustAPI?

BustAPI isn't just another web framework. It's a **hybrid engine** that fuses the developer experience of Python with the raw performance of Rust.

By running on top of **Actix-Web** (Rust) via **PyO3** bindings, BustAPI eliminates the bottlenecks typical of Python frameworks. It handles requests, routing, and concurrency in compiled Rust code, leaving Python to do what it does best: business logic.

> **"It feels like Flask/FastAPI, but runs like a compiled binary."**

## 🌌 Future-Proof Architecture

### 🚀 **Performance First**

- **~20k RPS**: Capable of handling massive loads on a single node.
- **Zero-Process Overhead**: Efficient, low-latency request handling.

### 🧠 **Intelligent Concurrency**

- **Native Async**: Built on Tokio, the industry-standard Rust async runtime.
- **Smart Worker Pool**: Rust manages the thread pool, automatically scaling to your CPU cores.

### 🛠️ **Developer Experience (DX)**

- **Hot Reload**: Instant feedback loop with `watchfiles` integration.
- **Type-Safe**: Built with modern Python typing in mind.
- **Auto-Docs**: Interactive Swagger/OpenAPI documentation generated automatically.

---

## 📦 Installation

Install the core framework:

```bash
pip install bustapi
```

### If you need ASGI / WSGI

Install with standard server compatibility (Uvicorn, Gunicorn, Hypercorn):

```bash
pip install "bustapi[server]"
```

Or go full throttle with all dev tools and benchmarks:

```bash
pip install "bustapi[full]"
```

---

## 🏁 Quick Start

Create `main.py`:

```python
from bustapi import BustAPI

app = BustAPI()

@app.route("/")
def home():
    return {"message": "Welcome to the future 🚀"}

@app.route("/users/<int:user_id>")
def get_user(user_id):
    return {"id": user_id, "status": "active"}

if __name__ == "__main__":
    # Hot reload enabled!
    app.run(debug=True)
```

Run it:

```bash
python main.py
```

Visit `http://127.0.0.1:5000` and confirm your entry into high-speed web development.

---

## 🔌 Server & Deployment

BustAPI is flexible. Use the ultra-fast internal Rust server, or bring your own.

### **Rust Engine (Default)**

Optimized for raw speed.

```bash
python main.py
```

### **ASGI (Uvicorn)**

```bash
uvicorn main:app.asgi_app --interface asgi3
```

### **WSGI (Gunicorn)**

```bash
gunicorn main:app
```

---

## 🛡️ Key Features

- **Rate Limiting**: Built-in, high-performance rate limiter protected by Rust.
- **Middleware**: Simple `@app.before_request` and `@app.after_request` hooks.
- **Blueprints**: Organizing extensive applications with ease.
- **Templates**: Integrated Jinja2 support.
- **Security**: Robust headers and CORS support out of the box.

### ✨ New in v0.5.0
- **FastAPI Compatibility**: Migrate easily with `Header`, `Cookie`, `Form`, `File`, and `UploadFile` support.
- **Context Globals**: Full support for Flask-style `g` and `current_app` proxies.
- **Background Tasks**: Fire-and-forget tasks with `BackgroundTasks`.
- **Response Aliases**: Use `JSONResponse`, `HTMLResponse`, etc., just like in FastAPI.

---

## Benchmarks at a Glance

| Framework           | Requests/Sec | Relative Speed | Memory (RAM) |
| :------------------ | :----------- | :------------- | :----------- |
| **BustAPI (v0.5)**  | **25,782**   | **🚀 100%**    | **~24 MB**   |
| Catzilla (v0.2)     | 15,727       | 💨 61%         | ~718 MB      |
| Flask (4 workers)   | 6,869        | 🐢 27%         | ~160 MB      |
| FastAPI (4 workers) | 1,867        | 🐢 7%          | ~237 MB      |

_(Benchmarks run on Python 3.13, Intel i5-8365U, 8 Cores, Ubuntu Linux)_

---

## 🤝 Contributing & Community

Join us in building the fastest Python framework ever created.

- **[Issues](https://github.com/GrandpaEJ/bustapi/issues)**: Report bugs or request features.
- **[Discussions](https://github.com/GrandpaEJ/bustapi/discussions)**: Ask questions and share ideas.

## 📄 License

[MIT](LICENSE) © 2025 GrandpaEJ.
