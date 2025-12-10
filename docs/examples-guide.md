# BustAPI Examples Guide

> Comprehensive examples demonstrating all features of BustAPI

## Table of Contents

1. [Getting Started](#getting-started)
2. [Routing Examples](#routing-examples)
3. [Request Handling](#request-handling)
4. [Response Types](#response-types)
5. [Async Operations](#async-operations)
6. [Database Integration](#database-integration)
7. [Blueprints & Organization](#blueprints--organization)
8. [Security & Authentication](#security--authentication)
9. [Rate Limiting](#rate-limiting)
10. [Error Handling](#error-handling)
11. [Middleware & Hooks](#middleware--hooks)
12. [Template Rendering](#template-rendering)
13. [Testing](#testing)
14. [Production Deployment](#production-deployment)

---

## Getting Started

### Minimal Application

```python
from bustapi import BustAPI

app = BustAPI()

@app.route('/')
def hello():
    return {'message': 'Hello, World!'}

if __name__ == '__main__':
    app.run()
```

### Application with Configuration

```python
from bustapi import BustAPI
import os

app = BustAPI(
    import_name='myapp',
    static_folder='assets',
    template_folder='views'
)

# Configuration
app.config['DEBUG'] = os.getenv('DEBUG', 'False') == 'True'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def index():
    return {'app': 'myapp', 'debug': app.config['DEBUG']}

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )
```

---

## Routing Examples

### Basic Routes

```python
from bustapi import BustAPI

app = BustAPI()

@app.route('/')
def index():
    return {'page': 'home'}

@app.route('/about')
def about():
    return {'page': 'about'}

@app.route('/contact')
def contact():
    return {'page': 'contact'}
```

### HTTP Method Routing

```python
# Using methods parameter
@app.route('/api/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        return {'items': []}
    elif request.method == 'POST':
        return {'created': True}, 201

# Using convenience decorators
@app.get('/items')
def get_items():
    return {'items': []}

@app.post('/items')
def create_item():
    return {'created': True}, 201

@app.put('/items/<int:item_id>')
def update_item(item_id):
    return {'updated': item_id}

@app.delete('/items/<int:item_id>')
def delete_item(item_id):
    return {'deleted': item_id}
```

### URL Parameters

```python
# String parameter (default)
@app.route('/users/<username>')
def user_profile(username):
    return {'username': username}

# Integer parameter
@app.route('/posts/<int:post_id>')
def get_post(post_id):
    return {'post_id': post_id, 'type': type(post_id).__name__}

# Float parameter
@app.route('/price/<float:amount>')
def show_price(amount):
    return {'price': amount, 'currency': 'USD'}

# Path parameter (matches slashes)
@app.route('/files/<path:filepath>')
def get_file(filepath):
    return {'path': filepath}

# Multiple parameters
@app.route('/users/<int:user_id>/posts/<int:post_id>')
def user_post(user_id, post_id):
    return {'user_id': user_id, 'post_id': post_id}
```

### Complex Routing

```python
# Nested routes with multiple parameters
@app.route('/api/<version>/users/<int:user_id>/posts/<int:post_id>')
def api_user_post(version, user_id, post_id):
    return {
        'api_version': version,
        'user_id': user_id,
        'post_id': post_id
    }

# Optional trailing slash
@app.route('/about/')
def about_trailing():
    return {'page': 'about'}

# Route with defaults
@app.route('/search')
@app.route('/search/<query>')
def search(query=''):
    return {'query': query or 'all'}
```

---

## Request Handling

### Query Parameters

```python
from bustapi import request

@app.route('/search')
def search():
    # Get single value
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    # Get multiple values
    tags = request.args.getlist('tag')

    return {
        'query': query,
        'page': page,
        'limit': limit,
        'tags': tags
    }

# Example: /search?q=python&page=2&limit=20&tag=web&tag=api
```

### Form Data

```python
@app.route('/submit', methods=['POST'])
def submit_form():
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Get all form data
    all_data = dict(request.form)

    return {
        'name': name,
        'email': email,
        'message': message,
        'all_data': all_data
    }
```

### JSON Data

```python
@app.route('/api/users', methods=['POST'])
def create_user():
    # Get JSON data
    data = request.json

    # Validate
    if not data:
        return {'error': 'No JSON data provided'}, 400

    if 'name' not in data:
        return {'error': 'Name is required'}, 400

    # Process
    user = {
        'id': 1,
        'name': data['name'],
        'email': data.get('email'),
        'age': data.get('age', 0)
    }

    return user, 201
```

### Headers

```python
@app.route('/api/data')
def get_data():
    # Get specific header
    auth = request.headers.get('Authorization')
    content_type = request.headers.get('Content-Type')
    user_agent = request.headers.get('User-Agent')

    # Check header existence
    has_auth = 'Authorization' in request.headers

    # Get all headers
    all_headers = dict(request.headers)

    return {
        'auth': auth,
        'content_type': content_type,
        'user_agent': user_agent,
        'has_auth': has_auth
    }
```

### Cookies

```python
@app.route('/get-cookie')
def get_cookie():
    # Get specific cookie
    session_id = request.cookies.get('session_id')
    user_pref = request.cookies.get('user_pref', 'default')

    # Get all cookies
    all_cookies = dict(request.cookies)

    return {
        'session_id': session_id,
        'user_pref': user_pref,
        'all_cookies': all_cookies
    }
```

### File Uploads

```python
@app.route('/upload', methods=['POST'])
def upload_file():
    # Get uploaded file
    file = request.files.get('file')

    if not file:
        return {'error': 'No file uploaded'}, 400

    # Save file
    filename = secure_filename(file.filename)
    file.save(f'uploads/{filename}')

    return {
        'filename': filename,
        'size': len(file.read())
    }
```

### Request Information

```python
@app.route('/request-info')
def request_info():
    return {
        'method': request.method,
        'url': request.url,
        'base_url': request.base_url,
        'path': request.path,
        'query_string': request.query_string.decode(),
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent,
        'referrer': request.referrer,
        'is_secure': request.is_secure,
        'is_json': request.is_json,
        'is_xhr': request.is_xhr()
    }
```

---

## Response Types

### JSON Responses

```python
from bustapi import jsonify

@app.route('/api/user')
def get_user():
    # Dictionary
    return jsonify({'id': 1, 'name': 'Alice'})

@app.route('/api/users')
def get_users():
    # List
    return jsonify([
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'}
    ])

@app.route('/api/status')
def status():
    # Keyword arguments
    return jsonify(status='ok', version='1.0.0')
```

### HTML Responses

```python
@app.route('/page')
def html_page():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Page</title></head>
    <body><h1>Hello, World!</h1></body>
    </html>
    '''

@app.route('/styled')
def styled_page():
    html = '''
    <html>
    <head>
        <style>
            body { font-family: Arial; margin: 40px; }
            h1 { color: #333; }
        </style>
    </head>
    <body>
        <h1>Styled Page</h1>
        <p>This is a styled HTML response.</p>
    </body>
    </html>
    '''
    return html
```

### Custom Status Codes

```python
@app.route('/created', methods=['POST'])
def create_resource():
    return {'id': 1, 'created': True}, 201

@app.route('/accepted', methods=['POST'])
def accept_job():
    return {'job_id': 123, 'status': 'accepted'}, 202

@app.route('/no-content', methods=['DELETE'])
def delete_resource():
    return '', 204
```

### Custom Headers

```python
from bustapi import make_response

@app.route('/custom-headers')
def custom_headers():
    response = make_response({'data': 'value'})
    response.headers['X-Custom-Header'] = 'CustomValue'
    response.headers['X-API-Version'] = '1.0'
    return response
```

### Cookies

```python
@app.route('/set-cookie')
def set_cookie():
    response = make_response({'message': 'Cookie set'})
    response.set_cookie(
        'session_id',
        'abc123',
        max_age=3600,
        secure=True,
        httponly=True,
        samesite='Lax'
    )
    return response

@app.route('/delete-cookie')
def delete_cookie():
    response = make_response({'message': 'Cookie deleted'})
    response.delete_cookie('session_id')
    return response
```

### Redirects

```python
from bustapi import redirect

@app.route('/old-url')
def old_url():
    return redirect('/new-url')

@app.route('/permanent-redirect')
def permanent():
    return redirect('/new-location', code=301)

@app.route('/external')
def external_redirect():
    return redirect('https://example.com')
```

### File Downloads

```python
from bustapi.core.helpers import send_file

@app.route('/download/<filename>')
def download(filename):
    return send_file(
        f'files/{filename}',
        as_attachment=True,
        attachment_filename=filename
    )

@app.route('/image/<image_name>')
def serve_image(image_name):
    return send_file(
        f'images/{image_name}',
        mimetype='image/png'
    )
```

---

## Async Operations

### Basic Async Handler

```python
import asyncio

@app.route('/async')
async def async_handler():
    await asyncio.sleep(1)
    return {'mode': 'async', 'waited': 1}
```

### Async Database Query

```python
import aiohttp

@app.route('/api/external')
async def fetch_external():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.example.com/data') as resp:
            data = await resp.json()
            return {'external_data': data}
```

### Multiple Async Operations

```python
@app.route('/api/combined')
async def combined_operations():
    # Run multiple async operations concurrently
    results = await asyncio.gather(
        fetch_user_data(),
        fetch_posts(),
        fetch_comments()
    )

    return {
        'user': results[0],
        'posts': results[1],
        'comments': results[2]
    }

async def fetch_user_data():
    await asyncio.sleep(0.1)
    return {'id': 1, 'name': 'Alice'}

async def fetch_posts():
    await asyncio.sleep(0.2)
    return [{'id': 1, 'title': 'Post 1'}]

async def fetch_comments():
    await asyncio.sleep(0.15)
    return [{'id': 1, 'text': 'Comment 1'}]
```

### Mixing Sync and Async

```python
# Sync route
@app.route('/sync')
def sync_route():
    return {'mode': 'sync'}

# Async route
@app.route('/async')
async def async_route():
    await asyncio.sleep(0.1)
    return {'mode': 'async'}

# Both work seamlessly in the same app
```

---

## Database Integration

### SQLite Example

```python
import sqlite3
from bustapi import BustAPI, jsonify, request

app = BustAPI()
DATABASE = 'app.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def before_request():
    request.db = get_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(request, 'db', None)
    if db is not None:
        db.close()

@app.route('/init-db')
def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    db.commit()
    db.close()
    return {'message': 'Database initialized'}

@app.route('/users')
def list_users():
    cursor = request.db.execute('SELECT * FROM users')
    users = [dict(row) for row in cursor.fetchall()]
    return jsonify(users)

@app.route('/users/<int:user_id>')
def get_user(user_id):
    cursor = request.db.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    if not user:
        return {'error': 'User not found'}, 404
    return jsonify(dict(user))

@app.post('/users')
def create_user():
    data = request.json
    try:
        cursor = request.db.execute(
            'INSERT INTO users (name, email) VALUES (?, ?)',
            (data['name'], data['email'])
        )
        request.db.commit()
        return {'id': cursor.lastrowid, 'name': data['name']}, 201
    except sqlite3.IntegrityError:
        return {'error': 'Email already exists'}, 400

@app.put('/users/<int:user_id>')
def update_user(user_id):
    data = request.json
    request.db.execute(
        'UPDATE users SET name = ?, email = ? WHERE id = ?',
        (data['name'], data['email'], user_id)
    )
    request.db.commit()
    return {'id': user_id, 'updated': True}

@app.delete('/users/<int:user_id>')
def delete_user(user_id):
    request.db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    request.db.commit()
    return {'deleted': True}
```

### PostgreSQL with psycopg2

```python
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = 'postgresql://user:password@localhost/dbname'

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.before_request
def before_request():
    request.db = get_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(request, 'db', None)
    if db is not None:
        db.close()

@app.route('/users')
def list_users():
    with request.db.cursor() as cursor:
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
    return jsonify(users)
```

---

## Blueprints & Organization

### Basic Blueprint

```python
from bustapi import Blueprint, BustAPI

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/status')
def status():
    return {'status': 'ok'}

@api.route('/version')
def version():
    return {'version': '1.0.0'}

# Create app and register
app = BustAPI()
app.register_blueprint(api)
```

### Multiple Blueprints

```python
# api_v1.py
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

@api_v1.route('/users')
def users_v1():
    return {'version': 1, 'users': []}

# api_v2.py
api_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')

@api_v2.route('/users')
def users_v2():
    return {'version': 2, 'users': [], 'pagination': {}}

# main.py
app = BustAPI()
app.register_blueprint(api_v1)
app.register_blueprint(api_v2)
```

### Nested Blueprints

```python
# admin/users.py
admin_users = Blueprint('admin_users', __name__, url_prefix='/users')

@admin_users.route('/')
def list_users():
    return {'users': []}

@admin_users.route('/<int:user_id>')
def get_user(user_id):
    return {'user_id': user_id}

# admin/__init__.py
admin = Blueprint('admin', __name__, url_prefix='/admin')
# Register nested blueprint
admin.register_blueprint(admin_users)

# main.py
app.register_blueprint(admin)
# Routes: /admin/users/, /admin/users/<id>
```

### Modular Application Structure

```
myapp/
├── app.py
├── config.py
├── blueprints/
│   ├── __init__.py
│   ├── api.py
│   ├── admin.py
│   └── public.py
├── models/
│   ├── __init__.py
│   └── user.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

**blueprints/api.py:**

```python
from bustapi import Blueprint, jsonify

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/status')
def status():
    return jsonify(status='ok')
```

**app.py:**

```python
from bustapi import BustAPI
from blueprints.api import api
from blueprints.admin import admin
from blueprints.public import public

app = BustAPI()

app.register_blueprint(api)
app.register_blueprint(admin)
app.register_blueprint(public)

if __name__ == '__main__':
    app.run()
```

---

## Security & Authentication

### Basic Authentication

```python
from functools import wraps
from bustapi import request, abort

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not check_auth(auth):
            abort(401, 'Authentication required')
        return f(*args, **kwargs)
    return decorated

def check_auth(auth_header):
    # Simple token check
    return auth_header == 'Bearer secret-token'

@app.route('/public')
def public():
    return {'message': 'Public endpoint'}

@app.route('/protected')
@require_auth
def protected():
    return {'message': 'Protected data'}
```

### JWT Authentication

```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'your-secret-key'

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_jwt(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            abort(401, 'Invalid authorization header')

        token = auth.split(' ')[1]
        user_id = verify_token(token)

        if not user_id:
            abort(401, 'Invalid or expired token')

        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated

@app.post('/login')
def login():
    data = request.json
    # Verify credentials (simplified)
    if data['username'] == 'admin' and data['password'] == 'password':
        token = create_token(user_id=1)
        return {'token': token}
    return {'error': 'Invalid credentials'}, 401

@app.route('/api/profile')
@require_jwt
def profile():
    return {'user_id': request.user_id, 'name': 'User'}
```

### CORS Configuration

```python
from bustapi import Security

security = Security(app)

# Allow all origins (development)
security.enable_cors(origins='*')

# Allow specific origins (production)
security.enable_cors(
    origins=['https://example.com', 'https://app.example.com'],
    methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['X-Total-Count'],
    max_age=86400
)
```

### Security Headers

```python
security = Security(app)
security.enable_secure_headers()

# Adds:
# X-Content-Type-Options: nosniff
# X-Frame-Options: SAMEORIGIN
# X-XSS-Protection: 1; mode=block
# Strict-Transport-Security: max-age=31536000
```

---

## Rate Limiting

### Basic Rate Limiting

```python
from bustapi import RateLimit

limiter = RateLimit(app)

@app.route('/api/data')
@limiter.limit('10/minute')
def get_data():
    return {'data': 'value'}
```

### Different Limits for Different Endpoints

```python
@app.route('/api/search')
@limiter.limit('100/hour')
def search():
    return {'results': []}

@app.route('/api/create', methods=['POST'])
@limiter.limit('5/minute')
def create():
    return {'created': True}, 201

@app.route('/api/expensive')
@limiter.limit('1/minute')
def expensive_operation():
    # Expensive operation
    return {'result': 'done'}
```

### Custom Key Functions

```python
def get_api_key():
    return request.headers.get('X-API-Key', 'anonymous')

@app.route('/api/custom')
@limiter.limit('100/hour', key_func=get_api_key)
def custom_limited():
    return {'data': 'value'}
```

### Rate Limit Error Handling

```python
@app.errorhandler(429)
def rate_limit_handler(e):
    return {
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.',
        'retry_after': 60
    }, 429
```

---

## Error Handling

### Custom Error Pages

```python
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return {'error': 'Resource not found'}, 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500
```

### Custom Exceptions

```python
class ValidationError(Exception):
    pass

class AuthenticationError(Exception):
    pass

@app.errorhandler(ValidationError)
def handle_validation(error):
    return {'error': str(error), 'type': 'validation'}, 400

@app.errorhandler(AuthenticationError)
def handle_auth(error):
    return {'error': str(error), 'type': 'authentication'}, 401

@app.route('/validate/<int:value>')
def validate(value):
    if value < 0:
        raise ValidationError('Value must be non-negative')
    return {'value': value}
```

### Global Error Handler

```python
@app.errorhandler(Exception)
def handle_exception(error):
    # Log the error
    app.logger.error(f'Unhandled exception: {error}')

    # Return generic error in production
    if app.config.get('DEBUG'):
        return {'error': str(error), 'type': type(error).__name__}, 500
    return {'error': 'Internal server error'}, 500
```

---

## Middleware & Hooks

### Request Logging

```python
import time

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_request(response):
    duration = time.time() - request.start_time
    print(f'{request.method} {request.path} - {response.status_code} ({duration:.3f}s)')
    return response
```

### Authentication Middleware

```python
@app.before_request
def check_authentication():
    # Skip auth for public routes
    if request.path in ['/', '/login', '/register']:
        return

    # Check authentication
    token = request.headers.get('Authorization')
    if not token:
        abort(401, 'Authentication required')
```

### Request ID Tracking

```python
import uuid

@app.before_request
def add_request_id():
    request.id = str(uuid.uuid4())

@app.after_request
def add_request_id_header(response):
    response.headers['X-Request-ID'] = request.id
    return response
```

### Database Connection Management

```python
@app.before_request
def connect_db():
    request.db = get_database_connection()

@app.teardown_request
def close_db(exception):
    db = getattr(request, 'db', None)
    if db is not None:
        db.close()
```

---

## Template Rendering

### Basic Template

```python
from bustapi import render_template

@app.route('/')
def index():
    return render_template('index.html',
        title='Home',
        message='Welcome to BustAPI'
    )
```

**templates/index.html:**

```html
<!DOCTYPE html>
<html>
  <head>
    <title>{{ title }}</title>
  </head>
  <body>
    <h1>{{ message }}</h1>
  </body>
</html>
```

### Template with Data

```python
@app.route('/users')
def users():
    users = [
        {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
        {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
    ]
    return render_template('users.html', users=users)
```

**templates/users.html:**

```html
<h1>Users</h1>
<ul>
  {% for user in users %}
  <li>{{ user.name }} ({{ user.email }})</li>
  {% endfor %}
</ul>
```

### Template Inheritance

**templates/base.html:**

```html
<!DOCTYPE html>
<html>
  <head>
    <title>{% block title %}Default{% endblock %}</title>
    <link rel="stylesheet" href="/static/style.css" />
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

---

## Testing

### Basic Tests

```python
import pytest
from myapp import app

@pytest.fixture
def client():
    return app.test_client()

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json['message'] == 'Hello'

def test_create_user(client):
    response = client.post('/users',
        data={'name': 'Alice', 'email': 'alice@example.com'},
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 201
    assert response.json['name'] == 'Alice'
```

### Testing with Database

```python
@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        init_db()
        yield app
        cleanup_db()

def test_user_crud(client):
    # Create
    response = client.post('/users', data={'name': 'Alice'})
    user_id = response.json['id']

    # Read
    response = client.get(f'/users/{user_id}')
    assert response.json['name'] == 'Alice'

    # Update
    response = client.put(f'/users/{user_id}', data={'name': 'Alice Updated'})
    assert response.json['updated'] == True

    # Delete
    response = client.delete(f'/users/{user_id}')
    assert response.status_code == 200
```

---

## Production Deployment

### Using Gunicorn

```bash
# Install
pip install gunicorn

# Run
gunicorn -w 4 -b 0.0.0.0:8000 myapp:app
```

### Using Uvicorn

```bash
# Install
pip install uvicorn

# Run
uvicorn myapp:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "bustapi", "run", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration

**.env:**

```
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db
PORT=8000
```

**config.py:**

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')
    PORT = int(os.getenv('PORT', 5000))
```

---

_For more examples, see the [examples directory](../examples/) in the repository._
