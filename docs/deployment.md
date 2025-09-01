# 🚀 BustAPI Production Deployment Guide

This guide covers deploying BustAPI applications to production environments with best practices for performance, security, and reliability.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [WSGI Deployment](#wsgi-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Performance Optimization](#performance-optimization)
- [Security Best Practices](#security-best-practices)
- [Monitoring & Logging](#monitoring--logging)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+ required
python --version

# Install BustAPI
pip install bustapi

# Verify installation
python -c "import bustapi; print('BustAPI installed successfully')"
```

### Basic Production Setup

```python
# app.py
from bustapi import BustAPI

app = BustAPI(
    title="My Production API",
    version="1.0.0",
    description="Production-ready BustAPI application"
)

@app.route('/')
def health_check():
    return {'status': 'healthy', 'version': '1.0.0'}

@app.route('/api/data')
def get_data():
    return {'data': 'production data'}

if __name__ == '__main__':
    # Development only
    app.run(host='127.0.0.1', port=8000, debug=False)
```

## 🔧 WSGI Deployment

### Using Gunicorn (Recommended)

Gunicorn is the recommended WSGI server for BustAPI production deployments.

#### Installation

```bash
pip install gunicorn
```

#### Basic Configuration

```bash
# Start with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# With custom configuration
gunicorn -w 4 -b 0.0.0.0:8000 --timeout 30 --keep-alive 2 app:app
```

#### Gunicorn Configuration File

Create `gunicorn.conf.py`:

```python
# gunicorn.conf.py
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = "bustapi_app"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn/bustapi.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
```

#### Start with Configuration

```bash
gunicorn -c gunicorn.conf.py app:app
```

### Using uWSGI

Alternative WSGI server option:

```bash
# Install uWSGI
pip install uwsgi

# Run with uWSGI
uwsgi --http :8000 --wsgi-file app.py --callable app --processes 4 --threads 2
```

### Using Uvicorn (ASGI)

For async support:

```bash
# Install Uvicorn
pip install uvicorn

# Run with Uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start application
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  bustapi:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
    volumes:
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - bustapi
    restart: unless-stopped

volumes:
  postgres_data:
```

### Multi-stage Build (Optimized)

```dockerfile
# Multi-stage Dockerfile for smaller images
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS Elastic Beanstalk

1. **Create `requirements.txt`**:
```txt
bustapi>=0.1.0
gunicorn>=20.0.0
```

2. **Create `.ebextensions/python.config`**:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
```

3. **Deploy**:
```bash
# Install EB CLI
pip install awsebcli

# Initialize and deploy
eb init
eb create production-api
eb deploy
```

#### Using AWS ECS with Fargate

```yaml
# task-definition.json
{
  "family": "bustapi-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "bustapi",
      "image": "your-account.dkr.ecr.region.amazonaws.com/bustapi:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/bustapi",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Platform

#### Using Cloud Run

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/bustapi', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/bustapi']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'bustapi'
      - '--image'
      - 'gcr.io/$PROJECT_ID/bustapi'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
```

### Heroku Deployment

1. **Create `Procfile`**:
```
web: gunicorn app:app
```

2. **Create `runtime.txt`**:
```
python-3.11.0
```

3. **Deploy**:
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-bustapi-app

# Deploy
git push heroku main
```

## ⚡ Performance Optimization

### Application-Level Optimizations

```python
# app.py - Production optimizations
from bustapi import BustAPI
import os

# Production configuration
app = BustAPI(
    title="Production API",
    version="1.0.0",
    # Disable docs in production for security
    docs_url=None if os.getenv('ENVIRONMENT') == 'production' else '/docs',
    redoc_url=None if os.getenv('ENVIRONMENT') == 'production' else '/redoc'
)

# Enable response compression
@app.middleware('http')
async def add_compression_headers(request, call_next):
    response = await call_next(request)
    response.headers['Content-Encoding'] = 'gzip'
    return response

# Add caching headers
@app.middleware('http')
async def add_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response
```

### Server Configuration

```python
# gunicorn.conf.py - Performance tuned
import multiprocessing

# Optimize worker count for your hardware
workers = min(multiprocessing.cpu_count() * 2 + 1, 8)

# Use sync workers for CPU-bound tasks
worker_class = "sync"

# Increase worker connections for I/O-bound tasks
worker_connections = 1000

# Optimize timeouts
timeout = 30
keepalive = 2

# Preload application for memory efficiency
preload_app = True

# Restart workers periodically
max_requests = 1000
max_requests_jitter = 50
```

### Database Optimization

```python
# database.py - Connection pooling
import sqlalchemy as sa
from sqlalchemy.pool import QueuePool

# Optimized database connection
engine = sa.create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## 🔒 Security Best Practices

### Environment Configuration

```python
# config.py
import os
from typing import Optional

class Config:
    # Security
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    ALLOWED_HOSTS: list = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    
    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    
    # Redis
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # API Keys
    API_KEY: Optional[str] = os.getenv('API_KEY')
    
    # Feature flags
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    TESTING: bool = os.getenv('TESTING', 'False').lower() == 'true'

config = Config()
```

### Security Middleware

```python
# security.py
from bustapi import BustAPI

def add_security_headers(app: BustAPI):
    @app.middleware('http')
    async def security_headers(request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        return response
```

### Rate Limiting

```python
# rate_limiting.py
from functools import wraps
import time
from collections import defaultdict

# Simple in-memory rate limiter (use Redis in production)
request_counts = defaultdict(list)

def rate_limit(max_requests: int = 100, window: int = 3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr
            now = time.time()
            
            # Clean old requests
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if now - req_time < window
            ]
            
            # Check rate limit
            if len(request_counts[client_ip]) >= max_requests:
                return {'error': 'Rate limit exceeded'}, 429
            
            # Record request
            request_counts[client_ip].append(now)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## 📊 Monitoring & Logging

### Structured Logging

```python
# logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/bustapi/app.log')
    ]
)

# Set JSON formatter
for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

### Health Check Endpoint

```python
# health.py
import psutil
import time
from bustapi import BustAPI

@app.route('/health')
def health_check():
    """Comprehensive health check"""
    try:
        # Check database connection
        # db_status = check_database()
        
        # Check Redis connection
        # redis_status = check_redis()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '1.0.0',
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': (disk.used / disk.total) * 100
            }
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }, 503

@app.route('/metrics')
def metrics():
    """Prometheus-compatible metrics"""
    # Implement Prometheus metrics
    pass
```

### Application Monitoring

```python
# monitoring.py
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            status = 'success'
            return result
        except Exception as e:
            status = 'error'
            raise
        finally:
            duration = time.time() - start_time
            
            # Log performance metrics
            logging.info(
                f"Performance: {func.__name__} took {duration:.3f}s - {status}",
                extra={
                    'function': func.__name__,
                    'duration': duration,
                    'status': status
                }
            )
    
    return wrapper
```

## 🔧 Troubleshooting

### Common Issues

#### 1. High Memory Usage

```bash
# Check memory usage
ps aux | grep gunicorn

# Monitor memory over time
watch -n 1 'ps aux | grep gunicorn | awk "{sum+=\$6} END {print sum/1024 \" MB\"}"'

# Solution: Restart workers periodically
# In gunicorn.conf.py:
max_requests = 1000
max_requests_jitter = 50
```

#### 2. Slow Response Times

```python
# Add timing middleware
@app.middleware('http')
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

#### 3. Database Connection Issues

```python
# Add connection retry logic
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

def create_db_engine_with_retry(database_url, max_retries=5):
    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url)
            # Test connection
            engine.execute("SELECT 1")
            return engine
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Performance Debugging

```bash
# Profile application
pip install py-spy
py-spy top --pid $(pgrep -f gunicorn)

# Monitor system resources
htop
iotop
nethogs

# Check application logs
tail -f /var/log/bustapi/app.log | jq '.'

# Monitor HTTP requests
tail -f /var/log/nginx/access.log
```

### Load Testing

```bash
# Install load testing tools
pip install locust

# Simple load test
locust -f locustfile.py --host=http://localhost:8000
```

```python
# locustfile.py
from locust import HttpUser, task, between

class BustAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def index_page(self):
        self.client.get("/")
    
    @task(1)
    def api_endpoint(self):
        self.client.get("/api/data")
```

## 📚 Additional Resources

- [BustAPI Documentation](../README.md)
- [Performance Benchmarks](../benchmarks/README.md)
- [Security Best Practices](security.md)
- [API Reference](api-reference.md)

---

**BustAPI** - High-performance Python web framework powered by Rust 🚀
