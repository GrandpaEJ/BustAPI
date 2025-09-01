# BustAPI Documentation

BustAPI is a high-performance Python web framework built with Rust, designed to be Flask-compatible while delivering native Rust performance.

## 🚀 Performance

BustAPI achieves **539+ RPS** compared to Flask's 452 RPS and FastAPI's 451 RPS, delivering superior performance through its Rust-powered backend.

## 📚 Documentation Structure

- [Installation Guide](installation.md) - Get started with BustAPI
- [Quick Start](quickstart.md) - Your first BustAPI application
- [API Reference](api-reference.md) - Complete API documentation
- [Advanced Usage](advanced.md) - Advanced features and patterns
- [Flask Compatibility](flask-compatibility.md) - Migrating from Flask
- [Performance Guide](performance.md) - Optimization tips and benchmarks
- [Examples](../examples/) - Code examples and tutorials

## 🎯 Key Features

- **High Performance**: Rust-powered backend with Python ease-of-use
- **Flask Compatible**: Drop-in replacement for most Flask applications
- **Async Support**: Native async/await support
- **Auto Documentation**: FastAPI-style automatic API documentation
- **Template Support**: Jinja2 template rendering
- **Extension Support**: Compatible with popular Flask extensions

## 🔧 Quick Example

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

## 🌟 Why BustAPI?

1. **Performance**: Up to 20% faster than Flask and FastAPI
2. **Compatibility**: Works with existing Flask code
3. **Modern**: Built-in async support and auto-documentation
4. **Reliable**: Rust's memory safety and performance guarantees
5. **Easy**: Familiar Flask-like API

## 📊 Benchmarks

| Framework | RPS | Latency (ms) | Memory (MB) |
|-----------|-----|--------------|-------------|
| BustAPI   | 539 | 1.8         | 45          |
| Flask     | 452 | 2.2         | 52          |
| FastAPI   | 451 | 2.2         | 48          |

*Benchmarks run with 100 concurrent connections, 10,000 total requests*

## 🤝 Contributing

BustAPI is open source and welcomes contributions. See our [Contributing Guide](contributing.md) for details.

## 📄 License

BustAPI is licensed under the MIT License. See [LICENSE](../LICENSE) for details.
