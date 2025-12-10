# Welcome to BustAPI

**BustAPI** is a high-performance Python web framework with the raw speed of [Rust](https://www.rust-lang.org/). Built on top of [PyO3](https://pyo3.rs/) and [Actix-web](https://actix.rs/).

[![PyPI version](https://badge.fury.io/py/bustapi.svg)](https://badge.fury.io/py/bustapi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Key Features

- **Rust-Powered Engine**: The core HTTP server, router, and request handling are implemented in Rust using Actix-web, providing blazing fast performance.
- **Async Support**: Native support for `async/await` syntax for high-concurrency workloads.
- **True Parallelism**: Leverages Python 3.13's free-threading mode (no GIL) for true multi-core parallel execution.
- **Secure by Default**: Built-in protection against Path Traversal, with optional Rate Limiting and Security Headers.
- **Developer Experience**: Includes Blueprints, Templates (Jinja2), and colorful Logging out of the box.

## ⚡ Performance

BustAPI allows write-heavy and compute-heavy logic to run in parallel without the GIL bottleneck, handling **100k+ requests per second** on modern hardware.

## 🛠️ Getting Started

Install with pip:

```bash
pip install bustapi
```

Create `app.py`:

```python
from bustapi import BustAPI

app = BustAPI()

@app.route("/")
def hello():
    return {"message": "Hello from BustAPI!"}

if __name__ == "__main__":
    app.run(debug=True)
```

Run it:

```bash
python app.py
```

Visit `http://127.0.0.1:5000` to see your API in action.

## 📚 Documentation Sections

- **[Installation](installation.md)**: Setup guide and requirements.
- **[Quickstart](quickstart.md)**: Build your first application in minutes.
- **[User Guide](user-guide/routing.md)**: Master routing, request handling, and templates.
- **[Advanced Features](advanced/async.md)**: Security, Async, and Deployment.
- **[API Reference](api-reference.md)**: Detailed API documentation.
