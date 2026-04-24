# BustAPI Complete API Reference

> **Version:** 0.3.1  
> **Last Updated:** 2025-12-10

## Table of Contents

1. [Core Application](#core-application)
2. [HTTP Request & Response](#http-request--response)
3. [Routing & Blueprints](#routing--blueprints)
4. [Security & Rate Limiting](#security--rate-limiting)
5. [Testing](#testing)
6. [Templating](#templating)
7. [Middleware & Hooks](#middleware--hooks)
8. [Error Handling](#error-handling)
9. [Helper Functions](#helper-functions)
10. [Auto-Documentation](#auto-documentation)

---

## Core Application

### `BustAPI`

The main application class for creating BustAPI web applications. Flask-compatible with high-performance Rust backend.

#### Constructor

```python
BustAPI(
    import_name: str = None,
    static_url_path: Optional[str] = None,
    static_folder: Optional[str] = None,
    template_folder: Optional[str] = None,
    instance_relative_config: bool = False,
    root_path: Optional[str] = None
)
```

**Parameters:**

- `import_name`: Name of the application package (default: module name)
- `static_url_path`: URL path for static files (default: `/static`)
- `static_folder`: Filesystem path to static files (default: `static`)
- `template_folder`: Filesystem path to templates (default: `templates`)
- `instance_relative_config`: Enable instance relative config
- `root_path`: Root path for the application

**Example:**

```python
from bustapi import BustAPI

app = BustAPI()
# or with custom configuration
app = BustAPI(
    import_name='myapp',
    static_folder='assets',
    template_folder='views'
)
```

#### Route Decorators

##### `@app.route(rule, **options)`

Register a view function for a URL rule.

**Parameters:**

- `rule` (str): URL pattern (e.g., `/users/<int:id>`)
- `methods` (List[str]): HTTP methods (default: `['GET']`)
- `endpoint` (str): Endpoint name (default: function name)

**Example:**

```python
@app.route('/')
def index():
    return {'message': 'Hello, World!'}

@app.route('/users/<int:user_id>', methods=['GET', 'POST'])
def user(user_id):
    return {'user_id': user_id}
```

##### Convenience Method Decorators

```python
@app.get(rule, **options)      # GET requests only
@app.post(rule, **options)     # POST requests only
@app.put(rule, **options)      # PUT requests only
@app.delete(rule, **options)   # DELETE requests only
@app.patch(rule, **options)    # PATCH requests only
@app.head(rule, **options)     # HEAD requests only
@app.options(rule, **options)  # OPTIONS requests only
```

**Example:**

```python
@app.get('/items')
def get_items():
    return {'items': []}

@app.post('/items')
def create_item():
    return {'id': 1}, 201
```

#### URL Parameters

BustAPI supports Flask-style URL parameters with type converters:

- `<name>` - String parameter (default)
- `<int:name>` - Integer parameter
- `<float:name>` - Float parameter
- `<path:name>` - Path parameter (matches slashes)
- `<uuid:name>` - UUID parameter

**Example:**

```python
@app.route('/users/<int:user_id>')
def get_user(user_id):
    # user_id is automatically converted to int
    return {'user_id': user_id, 'type': type(user_id).__name__}

@app.route('/files/<path:filepath>')
def get_file(filepath):
    # filepath can contain slashes
    return {'path': filepath}
```

#### Running the Application

##### `app.run(host, port, debug, **options)`

Run the application server.

**Parameters:**

- `host` (str): Hostname to bind to (default: `127.0.0.1`)
- `port` (int): Port to bind to (default: `5000`)
- `debug` (bool): Enable debug mode (default: `False`)
- `workers` (int): Number of worker threads (default: CPU count)
- `reload` (bool): Enable auto-reload on code changes (default: `False`)
- `server` (str): Server backend - `'rust'`, `'uvicorn'`, `'gunicorn'`, `'hypercorn'` (default: `'rust'`)

**Example:**

```python
# Development mode with auto-reload
app.run(debug=True, reload=True)

# Production mode with multiple workers
app.run(host='0.0.0.0', port=8000, workers=4)

# Using uvicorn server
app.run(server='uvicorn', port=8000)
```

##### `app.run_async(host, port, debug, **options)`

Run the application server asynchronously (for async applications).

**Example:**

```python
import asyncio

async def main():
    await app.run_async(host='0.0.0.0', port=8000)

asyncio.run(main())
```

#### Configuration

```python
# Set configuration values
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'your-secret-key'

# Access configuration
debug_mode = app.config.get('DEBUG', False)
```

#### Testing

##### `app.test_client(use_cookies=True, **kwargs)`

Create a test client for the application.

**Example:**

```python
def test_app():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
```

---

## HTTP Request & Response

### Request Object

The global `request` object provides access to incoming request data.

#### Importing

```python
from bustapi import request
```

#### Properties

##### Basic Request Info

```python
request.method          # HTTP method (GET, POST, etc.)
request.url             # Complete URL including query string
request.base_url        # Base URL without query string
request.path            # URL path component
request.query_string    # Raw query string as bytes
```

##### Request Data

```python
request.args            # Query parameters (ImmutableMultiDict)
request.form            # Form data (ImmutableMultiDict)
request.files           # Uploaded files (ImmutableMultiDict)
request.json            # Request body parsed as JSON
request.data            # Raw request body as bytes
request.values          # Combined args and form data
```

**Example:**

```python
@app.route('/search')
def search():
    query = request.args.get('q', 'default')
    page = request.args.get('page', 1, type=int)
    return {'query': query, 'page': page}

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    return {'received': data}
```

##### Headers & Cookies

```python
request.headers         # Request headers (EnvironHeaders)
request.cookies         # Request cookies (dict)
```

**Example:**

```python
@app.route('/api/data')
def get_data():
    auth_token = request.headers.get('Authorization')
    session_id = request.cookies.get('session_id')

    if not auth_token:
        return {'error': 'Unauthorized'}, 401

    return {'data': 'secret'}
```

##### Client Information

```python
request.remote_addr     # Client IP address
request.user_agent      # User agent string
request.referrer        # HTTP referrer
request.is_secure       # Whether request was made over HTTPS
```

##### Content Type Checks

```python
request.is_json         # Whether request has JSON content type
request.wants_json()    # Whether client prefers JSON response
request.wants_html()    # Whether client prefers HTML response
request.wants_xml()     # Whether client prefers XML response
request.is_xhr()        # Whether request was made via XMLHttpRequest
```

#### Methods

##### `request.get_data(cache=True, as_text=False, parse_form_data=False)`

Get request body data.

**Example:**

```python
@app.route('/upload', methods=['POST'])
def upload():
    raw_data = request.get_data(as_text=True)
    return {'length': len(raw_data)}
```

##### `request.get_json(force=False, silent=False, cache=True)`

Parse request body as JSON.

**Example:**

```python
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json(silent=True)
    if not data:
        return {'error': 'Invalid JSON'}, 400
    return {'user': data}, 201
```

### Response Objects

#### `Response`

Create HTTP responses with custom status codes and headers.

```python
from bustapi import Response

response = Response(
    response='Hello, World!',
    status=200,
    headers={'X-Custom-Header': 'value'},
    mimetype='text/plain',
    content_type='text/plain; charset=utf-8'
)
```

**Properties:**

```python
response.status_code    # HTTP status code
response.status         # Status code and reason phrase
response.headers        # Response headers (Headers dict)
response.content_type   # Content type header
response.data           # Response body as bytes
```

**Methods:**

```python
response.set_data(data)                 # Set response data
response.get_data(as_text=False)        # Get response data
response.set_cookie(key, value, ...)    # Set a cookie
response.delete_cookie(key, ...)        # Delete a cookie
```

**Example:**

```python
@app.route('/custom')
def custom_response():
    resp = Response('Custom response', status=200)
    resp.headers['X-Custom'] = 'Header'
    resp.set_cookie('session', 'abc123', max_age=3600)
    return resp
```

#### Response Helper Functions

##### `jsonify(*args, **kwargs)`

Create a JSON response.

```python
from bustapi import jsonify

@app.route('/api/data')
def get_data():
    return jsonify({'key': 'value'})
    # or
    return jsonify(key='value')
    # or
    return jsonify([1, 2, 3])
```

##### `make_response(*args)`

Create a Response object from various input types.

```python
from bustapi import make_response

@app.route('/example')
def example():
    # Response with status
    return make_response('Hello', 200)

    # Response with headers
    return make_response('Hello', {'X-Custom': 'Header'})

    # Response with status and headers
    return make_response('Hello', 200, {'X-Custom': 'Header'})
```

##### `redirect(location, code=302)`

Create a redirect response.

```python
from bustapi import redirect

@app.route('/old-page')
def old_page():
    return redirect('/new-page')

@app.route('/permanent')
def permanent_redirect():
    return redirect('/new-location', code=301)
```

##### `abort(code, description=None)`

Abort request with HTTP error code.

```python
from bustapi import abort

@app.route('/admin')
def admin():
    if not is_admin():
        abort(403, 'Admin access required')
    return {'message': 'Admin panel'}
```

#### HTTP Exceptions

```python
from bustapi.http.response import (
    BadRequest,           # 400
    Unauthorized,         # 401
    Forbidden,            # 403
    NotFound,             # 404
    MethodNotAllowed,     # 405
    InternalServerError   # 500
)

@app.route('/protected')
def protected():
    if not authenticated():
        raise Unauthorized('Please log in')
    return {'data': 'secret'}
```

---

## Routing & Blueprints

### Blueprints

Blueprints allow you to organize routes into reusable components.

#### Creating a Blueprint

```python
from bustapi import Blueprint

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/status')
def status():
    return {'status': 'ok'}

@api.route('/users')
def users():
    return {'users': []}
```

#### Blueprint Constructor

```python
Blueprint(
    name: str,
    import_name: str,
    static_folder: Optional[str] = None,
    static_url_path: Optional[str] = None,
    template_folder: Optional[str] = None,
    url_prefix: Optional[str] = None,
    subdomain: Optional[str] = None,
    url_defaults: Optional[Dict] = None,
    root_path: Optional[str] = None
)
```

#### Registering Blueprints

```python
# Register blueprint with app
app.register_blueprint(api)

# Register with custom prefix
app.register_blueprint(api, url_prefix='/api/v1')
```

#### Blueprint Route Decorators

Blueprints support all the same route decorators as the main app:

```python
@blueprint.route(rule, **options)
@blueprint.get(rule, **options)
@blueprint.post(rule, **options)
@blueprint.put(rule, **options)
@blueprint.delete(rule, **options)
@blueprint.patch(rule, **options)
@blueprint.head(rule, **options)
@blueprint.options(rule, **options)
```

#### Complete Blueprint Example

```python
from bustapi import Blueprint, BustAPI, jsonify

# Create blueprints
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
admin = Blueprint('admin', __name__, url_prefix='/admin')

# API routes
@api_v1.route('/status')
def api_status():
    return jsonify({'status': 'ok', 'version': 1})

@api_v1.route('/users')
def api_users():
    return jsonify({'users': ['alice', 'bob']})

# Admin routes
@admin.route('/dashboard')
def admin_dashboard():
    return '<h1>Admin Dashboard</h1>'

# Create app and register blueprints
app = BustAPI()
app.register_blueprint(api_v1)
app.register_blueprint(admin)

if __name__ == '__main__':
    app.run(debug=True)
```

---

## Security & Rate Limiting

### Security Extension

The Security extension provides CORS, security headers, and other security features.

#### Basic Usage

```python
from bustapi import BustAPI, Security

app = BustAPI()
security = Security(app)

# Enable CORS
security.enable_cors(
    origins='*',                    # Allowed origins
    methods=['GET', 'POST'],        # Allowed methods
    allow_headers=['Content-Type'], # Allowed headers
    expose_headers=[],              # Exposed headers
    max_age=3600                    # Preflight cache time
)

# Enable security headers
security.enable_secure_headers()
```

#### CORS Configuration

```python
# Allow specific origins
security.enable_cors(origins=['https://example.com', 'https://app.example.com'])

# Allow all origins (development only!)
security.enable_cors(origins='*')

# Custom configuration
security.enable_cors(
    origins=['https://example.com'],
    methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['X-Total-Count'],
    max_age=86400,
    supports_credentials=True
)
```

#### Security Headers

The `enable_secure_headers()` method adds the following headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### Rate Limiting

Protect your API endpoints from abuse with rate limiting.

#### Basic Usage

```python
from bustapi import BustAPI, RateLimit

app = BustAPI()
limiter = RateLimit(app)

@app.route('/api/resource')
@limiter.limit('5/minute')
def resource():
    return {'data': 'limited resource'}
```

#### Rate Limit Formats

```python
@limiter.limit('5/second')   # 5 requests per second
@limiter.limit('10/minute')  # 10 requests per minute
@limiter.limit('100/hour')   # 100 requests per hour
@limiter.limit('1000/day')   # 1000 requests per day
```

#### Custom Key Functions

```python
def get_user_id():
    # Custom logic to identify users
    return request.headers.get('X-User-ID', 'anonymous')

@app.route('/api/user-data')
@limiter.limit('10/minute', key_func=get_user_id)
def user_data():
    return {'data': 'user-specific data'}
```

#### Handling Rate Limit Errors

```python
@app.errorhandler(429)
def handle_rate_limit(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': str(e)
    }), 429
```

#### Complete Example

```python
from bustapi import BustAPI, RateLimit, jsonify

app = BustAPI()
limiter = RateLimit(app)

@app.route('/')
def home():
    return {'message': 'No rate limit'}

@app.route('/fast')
@limiter.limit('2/second')
def fast():
    return {'message': '2 requests per second allowed'}

@app.route('/slow')
@limiter.limit('1/minute')
def slow():
    return {'message': '1 request per minute allowed'}

@app.errorhandler(429)
def rate_limit_error(e):
    return jsonify(error=str(e)), 429

if __name__ == '__main__':
    app.run(debug=True)
```

---

## Testing

### Test Client

BustAPI provides a Flask-compatible test client for testing your applications.

#### Basic Usage

```python
from bustapi import BustAPI

app = BustAPI()

@app.route('/')
def index():
    return {'message': 'Hello, World!'}

# Create test client
client = app.test_client()

# Make requests
response = client.get('/')
assert response.status_code == 200
assert response.json['message'] == 'Hello, World!'
```

#### Test Client Methods

```python
client.get(path, **kwargs)      # GET request
client.post(path, **kwargs)     # POST request
client.put(path, **kwargs)      # PUT request
client.delete(path, **kwargs)   # DELETE request
client.patch(path, **kwargs)    # PATCH request
client.head(path, **kwargs)     # HEAD request
client.options(path, **kwargs)  # OPTIONS request
```

#### Request Parameters

```python
# Query parameters
response = client.get('/search', query_string={'q': 'test', 'page': 1})

# JSON data
response = client.post('/api/users',
    data={'name': 'Alice'},
    headers={'Content-Type': 'application/json'}
)

# Form data
response = client.post('/submit',
    data={'field': 'value'},
    content_type='application/x-www-form-urlencoded'
)

# Custom headers
response = client.get('/api/data',
    headers={'Authorization': 'Bearer token123'}
)
```

#### Test Response Object

```python
response.status_code    # HTTP status code
response.status         # Status string
response.data           # Response body as bytes
response.text           # Response body as text
response.json           # Response body as JSON
response.headers        # Response headers
response.is_json        # Whether response is JSON
```

#### Context Manager

```python
with app.test_client() as client:
    response = client.get('/')
    assert response.status_code == 200

    response = client.post('/api/data', data={'key': 'value'})
    assert response.json['key'] == 'value'
```

#### Complete Testing Example

```python
import pytest
from bustapi import BustAPI, jsonify

@pytest.fixture
def app():
    app = BustAPI()

    @app.route('/')
    def index():
        return {'message': 'Hello'}

    @app.route('/users/<int:user_id>')
    def get_user(user_id):
        return {'id': user_id, 'name': f'User {user_id}'}

    @app.post('/users')
    def create_user():
        data = request.json
        return {'id': 1, 'name': data['name']}, 201

    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json['message'] == 'Hello'

def test_get_user(client):
    response = client.get('/users/42')
    assert response.status_code == 200
    assert response.json['id'] == 42

def test_create_user(client):
    response = client.post('/users',
        data={'name': 'Alice'},
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 201
    assert response.json['name'] == 'Alice'
```

---

## Templating

BustAPI supports Jinja2 templates for rendering HTML.

### Basic Usage

```python
from bustapi import BustAPI, render_template

app = BustAPI(template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html',
        title='Welcome',
        user='Alice',
        items=['Fast', 'Safe', 'Easy']
    )
```

### Template Example

**templates/index.html:**

```html
<!DOCTYPE html>
<html>
  <head>
    <title>{{ title }}</title>
  </head>
  <body>
    <h1>Hello, {{ user }}!</h1>
    <ul>
      {% for item in items %}
      <li>{{ item }}</li>
      {% endfor %}
    </ul>
  </body>
</html>
```

### Template Functions

#### `render_template(template_name, **context)`

Render a template file.

```python
@app.route('/profile/<username>')
def profile(username):
    user_data = get_user(username)
    return render_template('profile.html',
        user=user_data,
        title=f'{username} Profile'
    )
```

### Template Inheritance

**templates/base.html:**

```html
<!DOCTYPE html>
<html>
  <head>
    <title>{% block title %}Default Title{% endblock %}</title>
  </head>
  <body>
    <nav>
      <a href="/">Home</a>
      <a href="/about">About</a>
    </nav>

    <main>{% block content %}{% endblock %}</main>

    <footer>&copy; 2025 BustAPI</footer>
  </body>
</html>
```

**templates/page.html:**

```html
{% extends "base.html" %} {% block title %}{{ page_title }}{% endblock %} {%
block content %}
<h1>{{ heading }}</h1>
<p>{{ content }}</p>
{% endblock %}
```

### Template Filters

Jinja2 provides many built-in filters:

```html
{{ name|upper }}
<!-- Uppercase -->
{{ text|lower }}
<!-- Lowercase -->
{{ items|length }}
<!-- Length -->
{{ price|round(2) }}
<!-- Round to 2 decimals -->
{{ date|default('N/A') }}
<!-- Default value -->
{{ html_content|safe }}
<!-- Mark as safe HTML -->
{{ user_input|escape }}
<!-- Escape HTML -->
```

---

## Middleware & Hooks

BustAPI provides hooks to run code before and after requests.

### Before Request

Run code before each request.

```python
@app.before_request
def before_request():
    # Runs before every request
    request.start_time = time.time()
    print(f'Request: {request.method} {request.path}')
```

### After Request

Run code after each request.

```python
@app.after_request
def after_request(response):
    # Runs after every request
    # Must return the response
    duration = time.time() - request.start_time
    print(f'Response: {response.status_code} ({duration:.3f}s)')

    # Add custom headers
    response.headers['X-Request-Time'] = str(duration)

    return response
```

### Teardown Request

Run code after each request, even if an exception occurred.

```python
@app.teardown_request
def teardown_request(exception):
    # Runs after every request, even on errors
    if exception:
        print(f'Error occurred: {exception}')

    # Cleanup resources
    if hasattr(request, 'db'):
        request.db.close()
```

### Teardown App Context

Run code when the application context is torn down.

```python
@app.teardown_appcontext
def teardown_appcontext(exception):
    # Cleanup application-level resources
    pass
```

### Complete Middleware Example

```python
import time
from bustapi import BustAPI, request, abort

app = BustAPI()

# Request counter
request_count = 0

@app.before_request
def start_timer():
    """Start request timer."""
    global request_count
    request_count += 1
    request.start_time = time.time()
    print(f'[{request.method}] {request.path} - Processing...')

@app.before_request
def check_auth():
    """Check authentication for protected routes."""
    if request.path.startswith('/admin'):
        auth = request.headers.get('Authorization')
        if auth != 'secret-token':
            abort(401, 'Unauthorized')

@app.after_request
def add_headers(response):
    """Add custom headers to response."""
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        response.headers['X-Request-Time'] = f'{duration:.4f}'

    response.headers['X-Request-Count'] = str(request_count)
    return response

@app.route('/')
def index():
    return {'message': 'Public route'}

@app.route('/admin/dashboard')
def admin():
    return {'message': 'Admin dashboard'}

if __name__ == '__main__':
    app.run(debug=True)
```

---

## Error Handling

### Error Handlers

Register custom error handlers for HTTP status codes or exceptions.

#### HTTP Status Code Handlers

```python
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Resource not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500
```

#### Exception Handlers

```python
class ValidationError(Exception):
    pass

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return {'error': str(error), 'type': 'validation_error'}, 400
```

### Using `abort()`

```python
from bustapi import abort

@app.route('/users/<int:user_id>')
def get_user(user_id):
    user = find_user(user_id)
    if not user:
        abort(404, 'User not found')
    return {'user': user}

@app.route('/admin')
def admin():
    if not is_admin():
        abort(403, 'Admin access required')
    return {'message': 'Admin panel'}
```

### Complete Error Handling Example

```python
from bustapi import BustAPI, abort, jsonify

app = BustAPI()

# Custom exception
class ValidationException(Exception):
    pass

class AuthenticationException(Exception):
    pass

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify(error='Resource not found', code=404), 404

@app.errorhandler(ValidationException)
def handle_validation(e):
    return jsonify(error=str(e), type='validation_error'), 400

@app.errorhandler(AuthenticationException)
def handle_auth(e):
    return jsonify(error=str(e), type='auth_error'), 401

# Routes
@app.route('/')
def home():
    return {
        'routes': [
            '/abort/<int:code> - trigger abort',
            '/error - raise exception',
            '/validate/<int:value> - validate value'
        ]
    }

@app.route('/abort/<int:code>')
def trigger_abort(code):
    abort(code)

@app.route('/error')
def trigger_error():
    raise Exception('Something went wrong!')

@app.route('/validate/<int:value>')
def validate(value):
    if value < 0:
        raise ValidationException('Value must be non-negative')
    return {'status': 'valid', 'value': value}

if __name__ == '__main__':
    app.run(debug=True)
```

---

## Helper Functions

### URL Helpers

#### `url_for(endpoint, **values)`

Generate URL for endpoint (simplified implementation).

```python
from bustapi import url_for

url = url_for('user_profile', user_id=42)
# Returns: '/users/42'
```

### Response Helpers

#### `redirect(location, code=302)`

Create redirect response.

```python
from bustapi import redirect

@app.route('/old-url')
def old_url():
    return redirect('/new-url')

@app.route('/permanent')
def permanent():
    return redirect('/new-location', code=301)
```

#### `send_file(path, mimetype=None, as_attachment=False)`

Send file as response.

```python
from bustapi.core.helpers import send_file

@app.route('/download/<filename>')
def download(filename):
    return send_file(f'files/{filename}', as_attachment=True)
```

#### `send_from_directory(directory, path)`

Send file from directory (with security checks).

```python
from bustapi.core.helpers import send_from_directory

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)
```

### Utility Helpers

#### `escape(text)`

Escape HTML special characters.

```python
from bustapi.core.helpers import escape

safe_text = escape('<script>alert("XSS")</script>')
# Returns: '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;'
```

#### `safe_join(directory, *pathnames)`

Safely join directory and path components.

```python
from bustapi.core.helpers import safe_join

safe_path = safe_join('/var/www', 'uploads', 'file.txt')
# Returns: '/var/www/uploads/file.txt' or None if unsafe
```

---

## Auto-Documentation

BustAPI can automatically generate OpenAPI documentation for your API.

### Basic Usage

```python
from bustapi import BustAPI, BustAPIDocs

app = BustAPI()

# Initialize documentation
docs = BustAPIDocs(
    app,
    title='My API',
    version='1.0.0',
    description='API documentation'
)

@app.route('/items')
def get_items():
    """
    Get list of items.

    Returns a list of all items in the inventory.
    """
    return {'items': []}

@app.route('/items/<int:item_id>')
def get_item(item_id):
    """
    Get specific item by ID.

    Args:
        item_id: The ID of the item to retrieve.
    """
    return {'id': item_id, 'name': f'Item {item_id}'}

if __name__ == '__main__':
    app.run(debug=True)
    # Swagger UI: http://localhost:5000/docs
    # ReDoc: http://localhost:5000/redoc
    # OpenAPI JSON: http://localhost:5000/openapi.json
```

### Documentation URLs

After initializing `BustAPIDocs`, the following endpoints are available:

- `/docs` - Swagger UI interface
- `/redoc` - ReDoc interface
- `/openapi.json` - OpenAPI specification (JSON)

### Documenting Routes

Use docstrings to document your routes:

```python
@app.get('/users')
def list_users():
    """
    List all users.

    Returns a paginated list of users in the system.

    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 10)

    Returns:
        200: List of users
        400: Invalid parameters
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    return {'users': [], 'page': page, 'limit': limit}

@app.post('/users')
def create_user():
    """
    Create a new user.

    Request Body:
        name (str): User's name
        email (str): User's email

    Returns:
        201: User created successfully
        400: Invalid input
    """
    data = request.json
    return {'id': 1, 'name': data['name']}, 201
```

---

## Complete Examples

### 1. Hello World

```python
from bustapi import BustAPI

app = BustAPI()

@app.route('/')
def index():
    return {'message': 'Hello, World!', 'framework': 'BustAPI'}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### 2. Async Handlers

```python
import asyncio
from bustapi import BustAPI

app = BustAPI()

@app.route('/sync')
def sync_handler():
    return {'mode': 'sync'}

@app.route('/async')
async def async_handler():
    await asyncio.sleep(0.1)
    return {'mode': 'async', 'waited': 0.1}

if __name__ == '__main__':
    app.run(port=5000)
```

### 3. Database Integration

```python
import sqlite3
from bustapi import BustAPI, jsonify, request

app = BustAPI()
DB_FILE = 'app.db'

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def connect_db():
    request.db = get_db()

@app.teardown_request
def close_db(exception):
    if hasattr(request, 'db'):
        request.db.close()

@app.route('/init-db')
def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)')
    conn.execute("INSERT INTO items (name) VALUES ('Rust')")
    conn.execute("INSERT INTO items (name) VALUES ('Python')")
    conn.commit()
    conn.close()
    return jsonify({'message': 'Database initialized'})

@app.route('/items')
def list_items():
    cursor = request.db.execute('SELECT * FROM items')
    items = [{'id': row['id'], 'name': row['name']} for row in cursor.fetchall()]
    return jsonify(items)

if __name__ == '__main__':
    app.run(debug=True)
```

### 4. Full-Featured API

```python
from bustapi import (
    BustAPI, Blueprint, jsonify, request, abort,
    RateLimit, Security, BustAPIDocs
)

app = BustAPI()

# Security
security = Security(app)
security.enable_cors(origins='*', methods=['GET', 'POST', 'PUT', 'DELETE'])
security.enable_secure_headers()

# Rate limiting
limiter = RateLimit(app)

# Documentation
docs = BustAPIDocs(app, title='My API', version='1.0.0')

# Blueprint
api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/status')
@limiter.limit('10/minute')
def status():
    """API status endpoint."""
    return jsonify({'status': 'ok', 'version': '1.0.0'})

@api.route('/users')
def list_users():
    """List all users."""
    return jsonify({'users': ['alice', 'bob']})

@api.route('/users/<int:user_id>')
def get_user(user_id):
    """Get user by ID."""
    return jsonify({'id': user_id, 'name': f'User {user_id}'})

@api.post('/users')
@limiter.limit('5/minute')
def create_user():
    """Create new user."""
    data = request.json
    if not data or 'name' not in data:
        abort(400, 'Name is required')
    return jsonify({'id': 1, 'name': data['name']}), 201

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify(error='Not found'), 404

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify(error='Rate limit exceeded'), 429

# Register blueprint
app.register_blueprint(api)

@app.route('/')
def index():
    return jsonify({
        'message': 'Welcome to My API',
        'docs': '/docs',
        'api': '/api/v1/status'
    })

if __name__ == '__main__':
    app.run(debug=True, port=8000)
```

---

## Configuration Reference

### Application Configuration

```python
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

### Server Options

```python
app.run(
    host='0.0.0.0',          # Bind to all interfaces
    port=8000,               # Port number
    debug=True,              # Debug mode
    workers=4,               # Number of workers
    reload=True,             # Auto-reload on changes
    server='rust'            # Server backend
)
```

### Available Servers

- `'rust'` - Built-in Rust server (default, fastest)
- `'uvicorn'` - ASGI server
- `'gunicorn'` - WSGI server
- `'hypercorn'` - ASGI server

---

## Performance Tips

1. **Use the Rust server** for maximum performance
2. **Enable multiple workers** in production
3. **Use async handlers** for I/O-bound operations
4. **Implement rate limiting** to protect your API
5. **Enable caching** for static content
6. **Use connection pooling** for databases
7. **Minimize middleware** overhead

---

## Version Information

```python
import bustapi

print(bustapi.__version__)           # '0.3.1'
print(bustapi.get_version())         # '0.3.1'
print(bustapi.get_debug_info())      # Detailed version info
```

---

_This documentation covers BustAPI version 0.3.1. For the latest updates, visit the [official documentation](https://grandpaej.github.io/BustAPI/)._
