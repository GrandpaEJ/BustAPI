# BustAPI Examples

This directory contains various examples demonstrating BustAPI features and usage patterns.

## 📁 Example Categories

### Basic Examples
- [`hello_world.py`](basic/hello_world.py) - Simple "Hello, World!" application
- [`routing.py`](basic/routing.py) - URL routing and parameters
- [`json_api.py`](basic/json_api.py) - JSON API responses
- [`request_handling.py`](basic/request_handling.py) - Handling different request types

### HTTP Methods
- [`http_methods.py`](http_methods/http_methods.py) - GET, POST, PUT, DELETE examples
- [`rest_api.py`](http_methods/rest_api.py) - RESTful API example
- [`file_upload.py`](http_methods/file_upload.py) - File upload handling

### Advanced Features
- [`async_handlers.py`](advanced/async_handlers.py) - Async/await support
- [`middleware.py`](advanced/middleware.py) - Custom middleware
- [`error_handling.py`](advanced/error_handling.py) - Error handling patterns
- [`blueprints.py`](advanced/blueprints.py) - Application blueprints

### Templates
- [`jinja_templates.py`](templates/jinja_templates.py) - Jinja2 template rendering
- [`template_inheritance.py`](templates/template_inheritance.py) - Template inheritance

### Flask Compatibility
- [`flask_migration.py`](flask_compat/flask_migration.py) - Migrating from Flask
- [`flask_extensions.py`](flask_compat/flask_extensions.py) - Using Flask extensions

### Real-World Applications
- [`todo_api.py`](real_world/todo_api.py) - Complete TODO API
- [`blog_api.py`](real_world/blog_api.py) - Blog API with authentication
- [`microservice.py`](real_world/microservice.py) - Microservice example

### Performance
- [`benchmarks.py`](performance/benchmarks.py) - Performance testing
- [`optimization.py`](performance/optimization.py) - Performance optimization tips

## 🚀 Running Examples

Each example can be run independently:

```bash
# Basic hello world
python examples/basic/hello_world.py

# REST API example
python examples/http_methods/rest_api.py

# Async handlers
python examples/advanced/async_handlers.py
```

## 📋 Requirements

Some examples may require additional dependencies:

```bash
# For template examples
pip install jinja2

# For database examples
pip install sqlalchemy

# For authentication examples
pip install pyjwt

# For testing examples
pip install pytest httpx
```

## 🎯 Learning Path

1. Start with [Basic Examples](basic/) to understand core concepts
2. Explore [HTTP Methods](http_methods/) for API development
3. Learn [Advanced Features](advanced/) for complex applications
4. Check [Flask Compatibility](flask_compat/) if migrating from Flask
5. Study [Real-World Applications](real_world/) for complete examples

## 💡 Tips

- Each example includes detailed comments explaining the code
- Examples are designed to be self-contained and runnable
- Check the docstrings for additional information
- Many examples include test cases you can run

## 🤝 Contributing Examples

Have a great BustAPI example? We'd love to include it! Please:

1. Follow the existing code style
2. Include comprehensive comments
3. Add a README if needed
4. Test your example thoroughly
5. Submit a pull request

## 📚 Additional Resources

- [Documentation](../docs/)
- [API Reference](../docs/api-reference.md)
- [Performance Guide](../docs/performance.md)
- [Flask Compatibility Guide](../docs/flask-compatibility.md)
