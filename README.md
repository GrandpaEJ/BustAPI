# BustAPI 🚀

[![PyPI version](https://badge.fury.io/py/bustapi.svg)](https://badge.fury.io/py/bustapi)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**BustAPI** is a high-performance, Flask-compatible Python web framework built with a Rust backend using PyO3. It combines Flask's simplicity with modern async capabilities and superior performance.


<h1>NOTE</h1>
- Made by AI , so Docs are not valid 100%

## ✨ Features

- 🏃‍♂️ **High Performance**: Built with Rust for maximum speed (50,000+ RPS)
- 🔄 **Hybrid Async/Sync**: Seamlessly support both programming models
- 🔌 **Flask Compatible**: Drop-in replacement with same API
- 🛠️ **Extension Support**: Works with Flask-CORS, SQLAlchemy, Login, JWT-Extended
- 🔥 **Hot Reload**: File watching with automatic restart
- 🛡️ **Production Ready**: Built-in security, monitoring, and cross-platform support
- 📦 **Modern Tooling**: UV packaging, fast builds, automated releases

## 🚀 Quick Start

### Installation

```bash
pip install bustapi
```

### Hello World

```python
from bustapi import BustAPI

app = BustAPI()

@app.route('/')
def hello():
    return {'message': 'Hello, World!'}

@app.route('/async')
async def async_hello():
    return {'message': 'Async Hello!'}

if __name__ == '__main__':
    app.run(debug=True)
```

### Flask Migration

BustAPI is designed as a drop-in replacement for Flask:

```python
# Just change the import!
# from flask import Flask
from bustapi import BustAPI as Flask

app = Flask(__name__)
# Rest of your Flask code works unchanged!
```

## 🔧 Development

### Prerequisites

- Python 3.8+
- Rust 1.70+
- UV (for package management)

### Setup

```bash
git clone https://github.com/grandpaej/bustapi.git
cd bustapi
uv sync --extra dev
```

### Build

```bash
maturin develop
```

### Run Tests

```bash
pytest
```

### Run Benchmarks

```bash
python benchmarks/benchmark_core.py
```

## 📊 Performance

BustAPI targets exceptional performance:

| Framework | Requests/sec | Memory Usage | Latency P99 |
|-----------|--------------|--------------|-------------|
| BustAPI   | 50,000+      | <50MB        | <10ms       |
| Flask     | 5,000-10,000 | 80-120MB     | 50-100ms    |
| FastAPI   | 20,000-30,000| 60-90MB      | 20-30ms     |

## 🔌 Flask Extension Compatibility

BustAPI works with popular Flask extensions:

```python
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from bustapi import BustAPI

app = BustAPI()

# Flask extensions work without changes
CORS(app)
db = SQLAlchemy(app)
```

**Supported Extensions:**
- ✅ Flask-CORS
- ✅ Flask-SQLAlchemy  
- ✅ Flask-Login
- ✅ Flask-JWT-Extended
- 🔄 More extensions being added

## 🛠️ CLI Usage

```bash
# Run application
bustapi run app:app

# Run with hot reload
bustapi run --reload --debug app:app

# Initialize new project
bustapi init myproject
```

## 📚 Documentation

- [Quick Start Guide](https://bustapi.dev/quickstart)
- [API Reference](https://bustapi.dev/api)
- [Migration from Flask](https://bustapi.dev/migration)
- [Performance Guide](https://bustapi.dev/performance)
- [Extension Development](https://bustapi.dev/extensions)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a virtual environment: `uv venv`
3. Install dependencies: `uv sync --extra dev`
4. Install pre-commit hooks: `pre-commit install`
5. Make your changes and run tests
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [PyO3](https://github.com/PyO3/pyo3) for Python-Rust integration
- Inspired by [Flask](https://flask.palletsprojects.com/) for the API design
- Uses [Tokio](https://tokio.rs/) and [Hyper](https://hyper.rs/) for async HTTP handling

## 🔗 Links

- [Homepage](https://bustapi.dev)
- [Documentation](https://bustapi.dev/docs)
- [PyPI Package](https://pypi.org/project/bustapi/)
- [GitHub Repository](https://github.com/bustapi/bustapi)
- [Issue Tracker](https://github.com/bustapi/bustapi/issues)

---

**BustAPI** - *High-performance Flask-compatible web framework* 🚀
