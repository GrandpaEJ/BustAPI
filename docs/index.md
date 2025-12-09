# 🚀 BustAPI - High-Performance Python Web Framework [EXPERIMENTAL]

<p align="center">
  <img src="https://github.com/GrandpaEJ/BustAPI/releases/download/v0.1.5/BustAPI.png" alt="BustAPI - Fast Python Web Framework" width="200">
</p>

<p align="center">
  <strong>Lightning-Fast Python Web Framework Powered by Rust | Flask Alternative | Async Support</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/bustapi/"><img src="https://img.shields.io/pypi/v/bustapi" alt="PyPI"></a>
  <a href="https://pypi.org/project/bustapi/"><img src="https://img.shields.io/pypi/pyversions/bustapi" alt="Python Versions"></a>
  <a href="https://github.com/GrandpaEJ/BustAPI/actions"><img src="https://img.shields.io/github/actions/workflow/status/GrandpaEJ/BustAPI/ci.yml" alt="CI"></a>
  <a href="https://github.com/GrandpaEJ/BustAPI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/GrandpaEJ/BustAPI" alt="License"></a>
  <a href="https://github.com/GrandpaEJ/BustAPI"><img src="https://img.shields.io/github/stars/GrandpaEJ/BustAPI" alt="Stars"></a>
  <img src="https://img.shields.io/badge/rust-1.70+-orange" alt="Rust">
</p>

# Welcome to BustAPI

**BustAPI** is a high-performance, Flask-compatible web framework for Python, built on top of Rust's **Actix-web**. It combines the developer-friendly API of Flask with the raw speed and concurrency of Rust.

## Key Features

- 🚀 **Blazing Fast**: Powered by Actix-web, one of the fastest web frameworks in the world.
- 🐍 **Flask Compatible**: Familiar API (`@app.route`, `request`, `render_template`).
- ⚡ **Async Support**: Native `async/await` support for high-concurrency workloads.
- 🧵 **Free-Threading**: Optimized for Python 3.13 (experimental) free-threaded mode (no GIL).
- 🧩 **Modular**: Support for Blueprints to organize large applications.
- 📄 **Auto-Documentation**: Built-in Swagger/ReDoc support.

## Performance

BustAPI is designed to handle thousands of requests per second (RPS) with minimal resource usage.

| Framework   | RPS (approx) | Memory (MB) |
| :---------- | :----------- | :---------- |
| **BustAPI** | **~19,600**  | **~54**     |
| Flask       | ~5,500       | ~180        |
| FastAPI     | ~2,100       | ~250        |

_Benchmarks run on standard hardware. See [Benchmarks](https://github.com/GrandpaEJ/bustapi/tree/main/benchmarks) for details._

## ⚡ Performance Benchmarks

BustAPI delivers **massive performance gains** over traditional Python web frameworks, achieving up to **175,923 requests per second** on dynamic routes - **54x faster** than Flask and **86x faster** than FastAPI in production benchmarks.

### Production Benchmark Results (4 workers, 100 connections)

| Endpoint          | BustAPI     | Flask | FastAPI | BustAPI Improvement |
| ----------------- | ----------- | ----- | ------- | ------------------- |
| **Plain Text**    | **19,929**  | 3,245 | 1,892   | **6.1x faster**     |
| **JSON Response** | **17,595**  | 3,241 | 1,900   | **5.4x faster**     |
| **Dynamic Path**  | **175,923** | 3,251 | 2,029   | **54.1x faster**    |

_Benchmarks: 15s duration, 4 threads, 100 connections using production servers (Gunicorn/Uvicorn)_

## ❓ What is BustAPI?

BustAPI is a revolutionary Python web framework that bridges the gap between Python's developer-friendly syntax and Rust's high-performance execution. Unlike traditional Python frameworks that are limited by the Global Interpreter Lock (GIL), BustAPI leverages Rust's Actix-Web runtime through PyO3 bindings, delivering **native compiled performance** while maintaining full Python compatibility.

Built as a drop-in replacement for Flask, BustAPI offers the same familiar API but with dramatically improved speed, making it ideal for high-throughput applications, APIs, and microservices where performance matters.

## 🚀 Why Choose BustAPI?

### Performance That Matters

- **50x+ Faster**: Handle thousands of concurrent requests with minimal latency
- **Production Ready**: Multi-worker support with built-in production server
- **Memory Efficient**: Rust's memory management eliminates Python's GC overhead

### Developer Experience

- **Flask Compatible**: Migrate existing Flask apps with zero code changes
- **Python Native**: Use familiar Python syntax and libraries
- **Async Support**: Built-in async/await for concurrent operations
- **Auto Documentation**: Generate OpenAPI specs automatically

### Enterprise Features

- **Type Safety**: Full type hints and validation
- **Extension Ecosystem**: Compatible with Flask extensions
- **Template Support**: Jinja2 rendering for dynamic content
- **Testing Tools**: Built-in test client for comprehensive testing

### Perfect For

- **APIs & Microservices**: High-throughput REST APIs
- **Web Applications**: Fast, scalable web apps
- **Real-time Applications**: Low-latency real-time features
- **Data Processing**: High-performance data pipelines
- **Edge Computing**: Lightweight, fast deployments

## 🎯 Key Features

- **🔥 Blazing Fast Performance**: Rust-powered backend delivers 50x+ faster request handling than traditional Python frameworks
- **🔄 Flask Compatible**: Drop-in replacement for Flask applications with zero code changes
- **⚡ Native Async Support**: Built-in async/await with Tokio runtime for concurrent request processing
- **📚 Automatic API Documentation**: FastAPI-style OpenAPI/Swagger UI generation for professional APIs
- **🎨 Template Rendering**: Jinja2 template engine support for dynamic web applications
- **🔧 Flask Extensions**: Compatible with popular Flask extensions ecosystem
- **🛡️ Type Safety**: Full type hints and Pydantic validation for robust applications
- **🌐 Complete HTTP Support**: All HTTP methods (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
- **🚀 Production Ready**: Built-in production server with multi-worker support
- **🐍 Python Native**: Pure Python API with familiar Flask-like syntax

## 🚀 Quick Start

### Installation

```bash
pip install bustapi
```

### Your First App

```python
from bustapi import BustAPI

app = BustAPI()

@app.route('/')
def hello():
    return {'message': 'Hello, World!'}

@app.route('/users/<int:user_id>')
def get_user(user_id):
    return {'user_id': user_id, 'name': f'User {user_id}'}

if __name__ == '__main__':
    app.run(debug=True)
```

Visit `http://127.0.0.1:8000` to see your app in action!

### Auto Documentation

```python
from bustapi import BustAPI

app = BustAPI(
    docs=True,
    title="My API",
    description="A high-performance API built with BustAPI",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc
    openapi_url="/openapi.json"
)

@app.get("/users")
def get_users():
    """Get all users from the system."""
    return {"users": []}

@app.post("/users")
def create_user():
    """Create a new user."""
    return {"message": "User created"}, 201
```

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

## 🔧 HTTP Methods

BustAPI supports all HTTP methods with convenient decorators:

```python
from bustapi import BustAPI

app = BustAPI()

@app.get('/items')
def get_items():
    return {'items': []}

@app.post('/items')
def create_item():
    return {'message': 'Item created'}, 201

@app.put('/items/<int:item_id>')
def update_item(item_id):
    return {'message': f'Item {item_id} updated'}

@app.delete('/items/<int:item_id>')
def delete_item(item_id):
    return {'message': f'Item {item_id} deleted'}

@app.patch('/items/<int:item_id>')
def patch_item(item_id):
    return {'message': f'Item {item_id} patched'}
```

## 🎨 Template Rendering

Full Jinja2 support with template inheritance:

```python
from bustapi import BustAPI, render_template

app = BustAPI()

@app.route('/')
def index():
    return render_template('index.html',
                         title='BustAPI App',
                         message='Welcome to BustAPI!')

@app.route('/users')
def users():
    users = [{'name': 'Alice'}, {'name': 'Bob'}]
    return render_template('users.html', users=users)
```

## 📊 Request Handling

```python
from bustapi import BustAPI, request

app = BustAPI()

@app.route('/data', methods=['POST'])
def handle_data():
    # JSON data
    json_data = request.get_json()

    # Form data
    form_data = request.form

    # Query parameters
    args = request.args

    # Headers
    headers = request.headers

    # Files
    files = request.files

    return {
        'json': json_data,
        'form': dict(form_data),
        'args': dict(args),
        'headers': dict(headers)
    }
```

## 💻 Platform Support

BustAPI is designed for maximum compatibility across platforms and deployment scenarios:

### Operating Systems

- **Linux**: Full support (Ubuntu, CentOS, Alpine, etc.)
- **macOS**: Full support (Intel and Apple Silicon)
- **Windows**: Full support via WSL or native builds

### Python Versions

- **Python 3.10+**: Latest features and optimizations

### Architecture Support

- **x86_64**: Full performance optimization
- **ARM64**: Native Apple Silicon and AWS Graviton support
- **Multi-core**: Automatic worker scaling

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

BustAPI is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with [PyO3](https://pyo3.rs/) for Python-Rust integration
- Powered by [Tokio](https://tokio.rs/) for async runtime
- Powered by [Actix-Web](https://actix.rs/) for high-performance web server
- Inspired by [Flask](https://flask.palletsprojects.com/) and [FastAPI](https://fastapi.tiangolo.com/)

---

**Made with ❤️ and ⚡ by the BustAPI team**
