# 🚀 BustAPI

**High-Performance Python Web Framework Powered by Rust**

BustAPI is a modern, fast Python web framework that combines the simplicity of Flask with the performance of Rust. Built with PyO3 and Tokio, it delivers **native Rust performance** while maintaining Python's ease of use.

## ⚡ Performance

BustAPI delivers **massive performance gains** over traditional Python frameworks, achieving up to **175,923 RPS** on dynamic routes - **54x faster** than Flask and **86x faster** than FastAPI.

### Production Benchmark Results (4 workers, 100 connections)

| Endpoint | BustAPI | Flask | FastAPI | BustAPI Improvement |
|----------|---------|-------|---------|-------------------|
| **Plain Text** | **19,929** | 3,245 | 1,892 | **6.1x faster** |
| **JSON Response** | **17,595** | 3,241 | 1,900 | **5.4x faster** |
| **Dynamic Path** | **175,923** | 3,251 | 2,029 | **54.1x faster** |

*Benchmarks: 15s duration, 4 threads, 100 connections using production servers (Gunicorn/Uvicorn)*

## 🎯 Key Features

- **🔥 High Performance**: Rust-powered backend with Python ease-of-use
- **🔄 Flask Compatible**: Drop-in replacement for most Flask applications  
- **⚡ Async Support**: Native async/await support with Tokio runtime
- **📚 Auto Documentation**: FastAPI-style automatic OpenAPI/Swagger UI
- **🎨 Template Support**: Jinja2 template rendering out of the box
- **🔧 Extension Support**: Compatible with popular Flask extensions
- **🛡️ Type Safety**: Full type hints and Pydantic integration
- **🌐 All HTTP Methods**: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS

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

## 🔄 Flask Migration

BustAPI is designed as a drop-in replacement for Flask:

```python
# Flask code
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        return jsonify({'users': []})
    return jsonify({'message': 'User created'}), 201

# BustAPI equivalent (same code!)
from bustapi import BustAPI, jsonify, request

app = BustAPI()

@app.route('/api/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        return jsonify({'users': []})
    return jsonify({'message': 'User created'}), 201
```

## 📚 Documentation & Examples

- **[📖 Full Documentation](docs/)** - Complete guides and API reference
- **[🎯 Examples](examples/)** - Working examples for all features
- **[🚀 Quick Start Guide](docs/quickstart.md)** - Get started in minutes
- **[🔧 API Reference](docs/api-reference.md)** - Complete API documentation

## 🏗️ Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Uvicorn

```bash
pip install uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

## 🧪 Testing

BustAPI includes a built-in test client:

```python
from bustapi.testing import TestClient

def test_app():
    client = TestClient(app)
    
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello, World!'}
    
    response = client.post('/users', json={'name': 'Alice'})
    assert response.status_code == 201
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

BustAPI is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with [PyO3](https://pyo3.rs/) for Python-Rust integration
- Powered by [Tokio](https://tokio.rs/) for async runtime
- Inspired by [Flask](https://flask.palletsprojects.com/) and [FastAPI](https://fastapi.tiangolo.com/)

---

**Made with ❤️ and ⚡ by the BustAPI team**
