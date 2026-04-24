# BustAPI Deployment & Performance Guide

> Complete guide for deploying and optimizing BustAPI applications in production

## Table of Contents

1. [Production Deployment](#production-deployment)
2. [Server Options](#server-options)
3. [Performance Optimization](#performance-optimization)
4. [Scaling Strategies](#scaling-strategies)
5. [Monitoring & Logging](#monitoring--logging)
6. [Security Best Practices](#security-best-practices)
7. [Docker Deployment](#docker-deployment)
8. [Cloud Deployment](#cloud-deployment)
9. [Load Balancing](#load-balancing)
10. [Benchmarking](#benchmarking)

---

## Production Deployment

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure proper logging
- [ ] Set up error monitoring
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Use environment variables
- [ ] Configure database connection pooling
- [ ] Set up health check endpoints
- [ ] Configure proper worker count
- [ ] Set up reverse proxy (nginx/caddy)
- [ ] Enable security headers
- [ ] Set up automated backups

### Environment Configuration

**.env (Production):**

```env
# Application
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis (for caching/sessions)
REDIS_URL=redis://localhost:6379/0

# Security
ALLOWED_HOSTS=example.com,www.example.com
CORS_ORIGINS=https://example.com,https://app.example.com

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO
```

### Application Configuration

**config.py:**

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    DATABASE_POOL_SIZE = int(os.getenv('DATABASE_POOL_SIZE', 10))

    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    WORKERS = int(os.getenv('WORKERS', 4))

    # Security
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    WORKERS = 1

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment."""
    env = os.getenv('ENVIRONMENT', 'development')
    return config.get(env, config['default'])
```

**app.py:**

```python
from bustapi import BustAPI
from config import get_config

def create_app():
    """Application factory."""
    config = get_config()

    app = BustAPI()
    app.config.from_object(config)

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Configure logging
    configure_logging(app)

    return app

def init_extensions(app):
    """Initialize extensions."""
    from extensions import db, security, limiter

    db.init_app(app)
    security.init_app(app)
    limiter.init_app(app)

def register_blueprints(app):
    """Register blueprints."""
    from blueprints.api import api
    from blueprints.admin import admin

    app.register_blueprint(api)
    app.register_blueprint(admin)

def configure_logging(app):
    """Configure logging."""
    import logging
    from logging.handlers import RotatingFileHandler

    if not app.config['DEBUG']:
        # File handler
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        workers=app.config['WORKERS']
    )
```

---

## Server Options

### 1. Rust Server (Built-in, Recommended)

**Best for:** Maximum performance, production use

```python
# Fastest option, uses Actix-web internally
app.run(
    host='0.0.0.0',
    port=8000,
    workers=4,
    server='rust'
)
```

**Benchmarks:**

- 50,000+ requests/second
- Sub-millisecond latency
- Low memory footprint

### 2. Uvicorn (ASGI)

**Best for:** Async applications, WebSocket support

```bash
# Install
pip install uvicorn

# Run
uvicorn myapp:app --host 0.0.0.0 --port 8000 --workers 4
```

```python
# In code
app.run(
    host='0.0.0.0',
    port=8000,
    workers=4,
    server='uvicorn'
)
```

### 3. Gunicorn (WSGI)

**Best for:** Traditional WSGI deployment, compatibility

```bash
# Install
pip install gunicorn

# Run
gunicorn -w 4 -b 0.0.0.0:8000 myapp:app
```

```python
# In code
app.run(
    host='0.0.0.0',
    port=8000,
    workers=4,
    server='gunicorn'
)
```

### 4. Hypercorn (ASGI)

**Best for:** HTTP/2, HTTP/3 support

```bash
# Install
pip install hypercorn

# Run
hypercorn myapp:app --bind 0.0.0.0:8000 --workers 4
```

### Server Comparison

| Server       | Type   | Performance | Async | HTTP/2 | WebSocket |
| ------------ | ------ | ----------- | ----- | ------ | --------- |
| Rust (Actix) | Native | ⭐⭐⭐⭐⭐  | ✅    | ✅     | ✅        |
| Uvicorn      | ASGI   | ⭐⭐⭐⭐    | ✅    | ❌     | ✅        |
| Gunicorn     | WSGI   | ⭐⭐⭐      | ❌    | ❌     | ❌        |
| Hypercorn    | ASGI   | ⭐⭐⭐⭐    | ✅    | ✅     | ✅        |

---

## Performance Optimization

### 1. Worker Configuration

```python
import multiprocessing

# Calculate optimal workers
workers = multiprocessing.cpu_count() * 2 + 1

app.run(
    host='0.0.0.0',
    port=8000,
    workers=workers
)
```

**Guidelines:**

- **CPU-bound tasks:** `workers = CPU cores`
- **I/O-bound tasks:** `workers = CPU cores * 2 + 1`
- **Mixed workload:** `workers = CPU cores * 1.5`

### 2. Database Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,              # Number of connections to maintain
    max_overflow=10,           # Additional connections when pool is full
    pool_timeout=30,           # Timeout for getting connection
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True         # Verify connections before use
)
```

### 3. Caching

**Response Caching:**

```python
from functools import lru_cache
import time

# In-memory cache
@lru_cache(maxsize=128)
def get_expensive_data(key):
    # Expensive operation
    time.sleep(1)
    return {'data': 'value'}

@app.route('/api/data/<key>')
def cached_data(key):
    return get_expensive_data(key)
```

**Redis Caching:**

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(timeout=300):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f'{f.__name__}:{args}:{kwargs}'

            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Get fresh data
            result = f(*args, **kwargs)

            # Store in cache
            redis_client.setex(
                cache_key,
                timeout,
                json.dumps(result)
            )

            return result
        return wrapper
    return decorator

@app.route('/api/users')
@cache_response(timeout=600)  # Cache for 10 minutes
def get_users():
    # Expensive database query
    return {'users': fetch_users_from_db()}
```

### 4. Async Operations

```python
import asyncio
import aiohttp

@app.route('/api/combined')
async def combined_data():
    # Run multiple operations concurrently
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
    async with aiohttp.ClientSession() as session:
        async with session.get('http://api.example.com/user') as resp:
            return await resp.json()
```

### 5. Response Compression

**Using nginx:**

```nginx
http {
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/json application/javascript;
}
```

### 6. Static File Optimization

**Serve static files with nginx:**

```nginx
location /static/ {
    alias /var/www/myapp/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 7. Database Query Optimization

```python
# Bad: N+1 queries
@app.route('/users')
def get_users():
    users = User.query.all()
    return [{
        'id': u.id,
        'name': u.name,
        'posts': [p.title for p in u.posts]  # N queries!
    } for u in users]

# Good: Eager loading
@app.route('/users')
def get_users():
    users = User.query.options(
        joinedload(User.posts)
    ).all()
    return [{
        'id': u.id,
        'name': u.name,
        'posts': [p.title for p in u.posts]  # Already loaded!
    } for u in users]
```

### 8. Pagination

```python
@app.route('/api/items')
def get_items():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Limit per_page to prevent abuse
    per_page = min(per_page, 100)

    offset = (page - 1) * per_page

    items = Item.query.limit(per_page).offset(offset).all()
    total = Item.query.count()

    return {
        'items': [item.to_dict() for item in items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }
```

---

## Scaling Strategies

### Horizontal Scaling

**Load Balancer Configuration (nginx):**

```nginx
upstream bustapi_backend {
    least_conn;  # Use least connections algorithm

    server 10.0.1.10:8000 weight=1 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8000 weight=1 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8000 weight=1 max_fails=3 fail_timeout=30s;
    server 10.0.1.13:8000 weight=1 max_fails=3 fail_timeout=30s;

    keepalive 32;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://bustapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Connection settings
        proxy_http_version 1.1;
        proxy_set_header Connection "";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### Vertical Scaling

**Optimize Resource Usage:**

```python
# Increase worker count
app.run(workers=16)  # For 8-core CPU

# Tune database pool
engine = create_engine(
    DATABASE_URL,
    pool_size=50,
    max_overflow=20
)
```

### Microservices Architecture

**Service Separation:**

```
┌─────────────┐
│   Gateway   │  (BustAPI)
└──────┬──────┘
       │
   ┌───┴───┬────────┬────────┐
   │       │        │        │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
│Auth │ │User │ │Post │ │File │
└─────┘ └─────┘ └─────┘ └─────┘
```

**API Gateway:**

```python
import httpx

@app.route('/api/user/<int:user_id>')
async def get_user(user_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'http://user-service:8001/users/{user_id}'
        )
        return response.json()

@app.route('/api/posts')
async def get_posts():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'http://post-service:8002/posts'
        )
        return response.json()
```

---

## Monitoring & Logging

### Application Logging

```python
import logging
from logging.handlers import RotatingFileHandler, SysLogHandler

def setup_logging(app):
    """Configure application logging."""

    # Create logs directory
    import os
    os.makedirs('logs', exist_ok=True)

    # File handler
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] %(message)s'
    ))

    # Error file handler
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] %(message)s\n'
        'Path: %(pathname)s:%(lineno)d\n'
        'Traceback:\n%(exc_info)s'
    ))

    # Add handlers
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)
```

### Request Logging

```python
import time
from bustapi import logging

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_request(response):
    duration = time.time() - request.start_time

    logging.log_request(
        request.method,
        request.path,
        response.status_code,
        duration
    )

    # Also log to file
    app.logger.info(
        f'{request.method} {request.path} '
        f'{response.status_code} {duration:.3f}s'
    )

    return response
```

### Error Monitoring (Sentry)

```python
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    environment=os.getenv('ENVIRONMENT', 'production'),
    traces_sample_rate=0.1,  # 10% of transactions
    integrations=[
        LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
    ]
)

@app.errorhandler(Exception)
def handle_exception(error):
    # Error is automatically sent to Sentry
    app.logger.error(f'Unhandled exception: {error}', exc_info=True)
    return {'error': 'Internal server error'}, 500
```

### Health Check Endpoints

```python
@app.route('/health')
def health_check():
    """Basic health check."""
    return {'status': 'healthy'}

@app.route('/health/detailed')
def detailed_health():
    """Detailed health check with dependencies."""
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'external_api': check_external_api()
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return {
        'status': 'healthy' if all_healthy else 'unhealthy',
        'checks': checks
    }, status_code

def check_database():
    try:
        db.session.execute('SELECT 1')
        return True
    except Exception:
        return False

def check_redis():
    try:
        redis_client.ping()
        return True
    except Exception:
        return False
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    duration = time.time() - request.start_time

    request_count.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()

    request_duration.labels(
        method=request.method,
        endpoint=request.path
    ).observe(duration)

    return response

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(), 200, {'Content-Type': 'text/plain'}
```

---

## Security Best Practices

### 1. HTTPS Configuration

**nginx SSL Configuration:**

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}
```

### 2. Security Headers

```python
from bustapi import Security

security = Security(app)
security.enable_secure_headers()

# Custom security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

### 3. Rate Limiting

```python
from bustapi import RateLimit

limiter = RateLimit(app)

# Global rate limit
@app.before_request
def global_rate_limit():
    if not limiter.check_limit('global', 1000, 60):
        abort(429, 'Global rate limit exceeded')

# Per-endpoint limits
@app.route('/api/expensive')
@limiter.limit('10/minute')
def expensive():
    return {'data': 'value'}
```

### 4. Input Validation

```python
from marshmallow import Schema, fields, ValidationError

class UserSchema(Schema):
    name = fields.Str(required=True, validate=lambda x: len(x) > 0)
    email = fields.Email(required=True)
    age = fields.Int(validate=lambda x: 0 <= x <= 150)

@app.post('/api/users')
def create_user():
    schema = UserSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return {'errors': err.messages}, 400

    # Data is validated
    user = create_user_in_db(data)
    return {'user': user}, 201
```

### 5. SQL Injection Prevention

```python
# Bad: SQL injection vulnerable
@app.route('/users/<username>')
def get_user_bad(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    result = db.execute(query)  # VULNERABLE!

# Good: Parameterized queries
@app.route('/users/<username>')
def get_user_good(username):
    query = "SELECT * FROM users WHERE username = ?"
    result = db.execute(query, (username,))  # Safe
```

### 6. CORS Configuration

```python
security.enable_cors(
    origins=['https://example.com'],  # Specific origins only
    methods=['GET', 'POST'],
    allow_headers=['Content-Type', 'Authorization'],
    max_age=3600
)
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "app.py"]
```

### docker-compose.yml

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:password@db:5432/dbname
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    networks:
      - app-network

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - app
    networks:
      - app-network

volumes:
  postgres-data:

networks:
  app-network:
    driver: bridge
```

---

## Cloud Deployment

### AWS Elastic Beanstalk

**.ebextensions/python.config:**

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
  aws:elasticbeanstalk:application:environment:
    ENVIRONMENT: production
    DEBUG: False
```

### Google Cloud Run

**cloudbuild.yaml:**

```yaml
steps:
  - name: "gcr.io/cloud-builders/docker"
    args: ["build", "-t", "gcr.io/$PROJECT_ID/bustapi-app", "."]
  - name: "gcr.io/cloud-builders/docker"
    args: ["push", "gcr.io/$PROJECT_ID/bustapi-app"]
  - name: "gcr.io/cloud-builders/gcloud"
    args:
      - "run"
      - "deploy"
      - "bustapi-app"
      - "--image=gcr.io/$PROJECT_ID/bustapi-app"
      - "--platform=managed"
      - "--region=us-central1"
      - "--allow-unauthenticated"
```

### Heroku

**Procfile:**

```
web: python app.py
```

**runtime.txt:**

```
python-3.11.0
```

---

## Benchmarking

### Load Testing with Apache Bench

```bash
# Simple benchmark
ab -n 10000 -c 100 http://localhost:8000/

# With keep-alive
ab -n 10000 -c 100 -k http://localhost:8000/

# POST requests
ab -n 1000 -c 10 -p data.json -T application/json http://localhost:8000/api/users
```

### Load Testing with wrk

```bash
# Basic test
wrk -t4 -c100 -d30s http://localhost:8000/

# With custom script
wrk -t4 -c100 -d30s -s script.lua http://localhost:8000/
```

**script.lua:**

```lua
wrk.method = "POST"
wrk.body   = '{"name": "test"}'
wrk.headers["Content-Type"] = "application/json"
```

### Performance Metrics

**Target Metrics:**

- **Throughput:** 10,000+ requests/second
- **Latency (p50):** < 10ms
- **Latency (p95):** < 50ms
- **Latency (p99):** < 100ms
- **Error Rate:** < 0.1%
- **CPU Usage:** < 70%
- **Memory Usage:** < 80%

---

_For more deployment examples and configurations, see the [deployment documentation](deployment.md)._
