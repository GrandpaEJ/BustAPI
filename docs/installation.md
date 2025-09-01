# Installation Guide

This guide will help you install BustAPI and get started with development.

## Prerequisites

- Python 3.8 or higher
- Rust 1.70+ (for building from source)
- pip or poetry for package management

## Installation Methods

### 1. Install from PyPI (Recommended)

```bash
pip install bustapi
```

### 2. Install from Source

```bash
# Clone the repository
git clone https://github.com/bustapi/bustapi.git
cd bustapi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install maturin

# Build and install
maturin develop --release
```

### 3. Development Installation

For development and contributing:

```bash
# Clone and setup
git clone https://github.com/bustapi/bustapi.git
cd bustapi

# Setup development environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
maturin develop
```

## Verify Installation

Create a simple test file to verify your installation:

```python
# test_installation.py
from bustapi import BustAPI

app = BustAPI()

@app.route('/')
def hello():
    return {'message': 'BustAPI is working!'}

if __name__ == '__main__':
    print("Starting BustAPI test server...")
    app.run(host='127.0.0.1', port=8000, debug=True)
```

Run the test:

```bash
python test_installation.py
```

Visit `http://127.0.0.1:8000` in your browser. You should see:

```json
{"message": "BustAPI is working!"}
```

## Optional Dependencies

### For Template Rendering

```bash
pip install jinja2
```

### For Database Support

```bash
pip install sqlalchemy
```

### For CORS Support

```bash
pip install flask-cors
```

### For Development

```bash
pip install pytest pytest-asyncio httpx
```

## Docker Installation

You can also run BustAPI in Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
```

## Troubleshooting

### Common Issues

1. **Rust not found**: Install Rust from https://rustup.rs/
2. **Maturin not found**: `pip install maturin`
3. **Permission errors**: Use virtual environment
4. **Build failures**: Ensure you have the latest Rust version

### Getting Help

- Check our [FAQ](faq.md)
- Open an issue on [GitHub](https://github.com/bustapi/bustapi/issues)
- Join our [Discord community](https://discord.gg/bustapi)

## Next Steps

- Read the [Quick Start Guide](quickstart.md)
- Explore [Examples](../examples/)
- Check out the [API Reference](api-reference.md)
