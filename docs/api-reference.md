# API Reference

Complete API reference for BustAPI framework.

## Core Classes

### BustAPI

The main application class for creating BustAPI applications.

```python
from bustapi import BustAPI

app = BustAPI(
    title="My API",
    description="API description",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

#### Parameters

- `title` (str, optional): API title for documentation
- `description` (str, optional): API description
- `version` (str, optional): API version
- `docs_url` (str, optional): Swagger UI URL path
- `redoc_url` (str, optional): ReDoc URL path
- `openapi_url` (str, optional): OpenAPI schema URL path

#### Methods

##### `route(path, methods=None, **options)`

Decorator to register a route handler.

```python
@app.route('/users/<int:user_id>', methods=['GET', 'POST'])
def handle_user(user_id):
    return {'user_id': user_id}
```

##### `get(path, **options)`, `post(path, **options)`, etc.

HTTP method-specific decorators.

```python
@app.get('/users')
def get_users():
    return {'users': []}

@app.post('/users')
def create_user():
    return {'message': 'User created'}, 201
```

##### `run(host='127.0.0.1', port=8000, debug=False)`

Run the development server.

```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

##### `add_middleware(middleware_class, **options)`

Add middleware to the application.

```python
from bustapi.middleware import CORSMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

##### `errorhandler(status_code)`

Register error handlers.

```python
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found'}, 404
```

## Request Handling

### Request Object

Access request data through the global `request` object.

```python
from bustapi import request

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
    
    return {'received': 'ok'}
```

#### Properties

- `method`: HTTP method (GET, POST, etc.)
- `url`: Full request URL
- `path`: URL path
- `query_string`: Raw query string
- `headers`: Request headers
- `form`: Form data (multipart/form-data)
- `args`: Query parameters
- `files`: Uploaded files
- `json`: JSON data (if Content-Type is application/json)

#### Methods

##### `get_json(force=False, silent=False)`

Parse JSON data from request body.

```python
data = request.get_json()
```

##### `get_data(as_text=False)`

Get raw request body data.

```python
raw_data = request.get_data()
text_data = request.get_data(as_text=True)
```

## Response Handling

### Response Functions

#### `jsonify(**kwargs)`

Create JSON response.

```python
from bustapi import jsonify

@app.route('/api/data')
def get_data():
    return jsonify(message="Hello", status="success")
```

#### `make_response(response, status=200, headers=None)`

Create custom response.

```python
from bustapi import make_response

@app.route('/custom')
def custom_response():
    response = make_response({'data': 'custom'})
    response.headers['X-Custom-Header'] = 'value'
    return response
```

#### `render_template(template_name, **context)`

Render Jinja2 template.

```python
from bustapi import render_template

@app.route('/')
def index():
    return render_template('index.html', title='Home')
```

### Response Formats

#### JSON Response

```python
@app.route('/json')
def json_response():
    return {'message': 'Hello, JSON!'}
```

#### Text Response

```python
@app.route('/text')
def text_response():
    return 'Hello, World!'
```

#### HTML Response

```python
@app.route('/html')
def html_response():
    return '<h1>Hello, HTML!</h1>'
```

#### Custom Status Code

```python
@app.route('/created', methods=['POST'])
def create_resource():
    return {'message': 'Created'}, 201
```

#### Custom Headers

```python
@app.route('/headers')
def custom_headers():
    response = make_response({'data': 'test'})
    response.headers['X-API-Version'] = '1.0'
    return response
```

## URL Routing

### Route Parameters

#### String Parameters

```python
@app.route('/users/<username>')
def show_user(username):
    return {'username': username}
```

#### Integer Parameters

```python
@app.route('/posts/<int:post_id>')
def show_post(post_id):
    return {'post_id': post_id}
```

#### Float Parameters

```python
@app.route('/price/<float:price>')
def show_price(price):
    return {'price': price}
```

#### Path Parameters

```python
@app.route('/files/<path:filename>')
def show_file(filename):
    return {'filename': filename}
```

### HTTP Methods

```python
@app.route('/resource', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_resource():
    if request.method == 'GET':
        return {'action': 'read'}
    elif request.method == 'POST':
        return {'action': 'create'}
    elif request.method == 'PUT':
        return {'action': 'update'}
    elif request.method == 'DELETE':
        return {'action': 'delete'}
```

## Error Handling

### Built-in Error Handlers

```python
from bustapi import abort

@app.route('/users/<int:user_id>')
def get_user(user_id):
    if user_id < 1:
        abort(400, description="Invalid user ID")
    
    if user_id > 1000:
        abort(404, description="User not found")
    
    return {'user_id': user_id}
```

### Custom Error Handlers

```python
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Resource not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500

@app.errorhandler(ValueError)
def handle_value_error(error):
    return {'error': str(error)}, 400
```

## Configuration

### Application Configuration

```python
app = BustAPI()

# Set configuration
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['DATABASE_URL'] = 'sqlite:///app.db'

# Access configuration
debug_mode = app.config.get('DEBUG', False)
```

### Environment Variables

```python
import os

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-key')
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
```

## Middleware

### CORS Middleware

```python
from bustapi.middleware import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Custom Middleware

```python
class CustomMiddleware:
    def __init__(self, app, **kwargs):
        self.app = app
        
    def __call__(self, request):
        # Process request
        response = self.app(request)
        # Process response
        return response

app.add_middleware(CustomMiddleware)
```

## Testing

### Test Client

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

## Performance

### Async Support

```python
@app.route('/async')
async def async_handler():
    # Async operations
    result = await some_async_operation()
    return {'result': result}
```

### Optimization Tips

1. Use appropriate HTTP methods
2. Implement proper caching headers
3. Minimize response payload size
4. Use connection pooling for databases
5. Enable compression middleware
6. Use async handlers for I/O operations

## Deployment

### Production Server

```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Using Uvicorn
pip install uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```
