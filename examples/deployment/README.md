# BustAPI Deployment Examples

This directory contains production-ready deployment examples and configurations for BustAPI applications.

## 📁 Directory Structure

```
deployment/
├── README.md                 # This file
├── production_app.py         # Production-ready BustAPI application
├── docker/                   # Docker deployment
│   ├── Dockerfile           # Production Dockerfile
│   ├── docker-compose.yml   # Complete stack with DB, Redis, Nginx
│   ├── gunicorn.conf.py     # Gunicorn configuration
│   └── requirements.txt     # Production dependencies
├── kubernetes/              # Kubernetes deployment
│   ├── deployment.yaml      # K8s deployment
│   ├── service.yaml         # K8s service
│   ├── ingress.yaml         # K8s ingress
│   └── configmap.yaml       # K8s configuration
├── aws/                     # AWS deployment
│   ├── eb-config/           # Elastic Beanstalk
│   ├── ecs-fargate/         # ECS Fargate
│   └── lambda/              # AWS Lambda
└── monitoring/              # Monitoring setup
    ├── prometheus.yml       # Prometheus config
    └── grafana/             # Grafana dashboards
```

## 🚀 Quick Start

### 1. Docker Deployment (Recommended)

```bash
# Clone the repository
git clone <your-repo>
cd examples/deployment/docker

# Set environment variables
export SECRET_KEY="your-super-secret-key"
export REDIS_PASSWORD="your-redis-password"

# Start the complete stack
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f bustapi
```

**Services included:**
- **BustAPI**: Main application (port 8000)
- **PostgreSQL**: Database (port 5432)
- **Redis**: Cache (port 6379)
- **Nginx**: Reverse proxy (ports 80/443)
- **Prometheus**: Metrics (port 9090)
- **Grafana**: Dashboards (port 3000)

### 2. Production Application

The `production_app.py` demonstrates a production-ready BustAPI application with:

- **Security headers** and middleware
- **Health checks** (`/health`, `/ready`, `/live`)
- **Metrics endpoint** (`/metrics`) for Prometheus
- **Structured logging** with request tracking
- **Error handling** with proper HTTP status codes
- **Environment-based configuration**

```python
# Key features
@app.middleware('http')
async def add_security_headers(request, call_next):
    # Security headers implementation
    pass

@app.route('/health')
def health_check():
    # Comprehensive health check
    return {'status': 'healthy', 'timestamp': time.time()}
```

### 3. Environment Configuration

Create a `.env` file:

```bash
# .env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/bustapi_db
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🐳 Docker Deployment

### Single Container

```bash
# Build image
docker build -t bustapi-app .

# Run container
docker run -d \
  --name bustapi \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e SECRET_KEY=your-secret-key \
  bustapi-app
```

### Full Stack with Docker Compose

```bash
# Start all services
docker-compose up -d

# Scale application
docker-compose up -d --scale bustapi=3

# Update application
docker-compose build bustapi
docker-compose up -d bustapi

# Backup database
docker-compose exec db pg_dump -U bustapi bustapi_db > backup.sql

# View metrics
open http://localhost:9090  # Prometheus
open http://localhost:3000  # Grafana (admin/admin)
```

## ☸️ Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Verify cluster access
kubectl cluster-info
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace bustapi

# Apply configurations
kubectl apply -f kubernetes/ -n bustapi

# Check deployment
kubectl get pods -n bustapi
kubectl get services -n bustapi

# View logs
kubectl logs -f deployment/bustapi -n bustapi

# Scale deployment
kubectl scale deployment bustapi --replicas=5 -n bustapi
```

### Ingress Configuration

```yaml
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bustapi-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: bustapi-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: bustapi-service
            port:
              number: 80
```

## ☁️ Cloud Deployment

### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize application
eb init bustapi-app

# Create environment
eb create production

# Deploy
eb deploy

# View logs
eb logs

# SSH to instance
eb ssh
```

### AWS ECS Fargate

```bash
# Build and push image
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-west-2.amazonaws.com
docker build -t bustapi .
docker tag bustapi:latest <account>.dkr.ecr.us-west-2.amazonaws.com/bustapi:latest
docker push <account>.dkr.ecr.us-west-2.amazonaws.com/bustapi:latest

# Create ECS service
aws ecs create-service --cli-input-json file://ecs-service.json
```

### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/bustapi
gcloud run deploy --image gcr.io/PROJECT_ID/bustapi --platform managed
```

### Heroku

```bash
# Create Procfile
echo "web: gunicorn production_app:app" > Procfile

# Deploy
heroku create your-bustapi-app
git push heroku main

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ENVIRONMENT=production
```

## 📊 Monitoring & Observability

### Health Checks

The production app includes multiple health check endpoints:

- **`/health`**: Comprehensive health check with system metrics
- **`/ready`**: Readiness check for container orchestration
- **`/live`**: Liveness check for container orchestration
- **`/metrics`**: Prometheus-compatible metrics

### Prometheus Metrics

```bash
# View metrics
curl http://localhost:8000/metrics

# Example output:
# bustapi_info{version="1.0.0",environment="production"} 1
# bustapi_uptime_seconds 3600
# bustapi_cpu_percent 15.2
# bustapi_memory_percent 45.8
```

### Grafana Dashboards

Access Grafana at `http://localhost:3000` (admin/admin) to view:

- **Application Performance**: Response times, throughput, error rates
- **System Metrics**: CPU, memory, disk usage
- **Business Metrics**: User activity, API usage patterns

### Log Aggregation

```python
# Structured logging example
import structlog

logger = structlog.get_logger()

@app.middleware('http')
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    logger.info(
        "request_processed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=time.time() - start_time
    )
    
    return response
```

## 🔒 Security Best Practices

### Environment Variables

```bash
# Never commit secrets to version control
# Use environment variables or secret management

# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id prod/bustapi/database

# Kubernetes Secrets
kubectl create secret generic bustapi-secrets \
  --from-literal=secret-key=your-secret-key \
  --from-literal=database-url=postgresql://...
```

### Security Headers

The production app automatically adds security headers:

```python
response.headers['X-Content-Type-Options'] = 'nosniff'
response.headers['X-Frame-Options'] = 'DENY'
response.headers['X-XSS-Protection'] = '1; mode=block'
response.headers['Strict-Transport-Security'] = 'max-age=31536000'
```

### Rate Limiting

```python
# Example rate limiting middleware
from collections import defaultdict
import time

request_counts = defaultdict(list)

@app.middleware('http')
async def rate_limit(request, call_next):
    client_ip = request.client.host
    now = time.time()
    
    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if now - req_time < 3600  # 1 hour window
    ]
    
    # Check limit
    if len(request_counts[client_ip]) >= 1000:  # 1000 requests per hour
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    
    request_counts[client_ip].append(now)
    return await call_next(request)
```

## 🔧 Performance Tuning

### Gunicorn Configuration

```python
# gunicorn.conf.py
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
```

### Database Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Caching

```python
import redis

# Redis connection
redis_client = redis.from_url(REDIS_URL)

@app.middleware('http')
async def cache_middleware(request, call_next):
    # Check cache
    cache_key = f"cache:{request.url.path}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return JSONResponse(content=json.loads(cached))
    
    # Process request
    response = await call_next(request)
    
    # Cache response
    if response.status_code == 200:
        redis_client.setex(cache_key, 300, response.body)  # 5 min cache
    
    return response
```

## 🚨 Troubleshooting

### Common Issues

1. **High Memory Usage**
   ```bash
   # Monitor memory
   docker stats bustapi
   
   # Restart workers periodically
   # In gunicorn.conf.py: max_requests = 1000
   ```

2. **Database Connection Errors**
   ```bash
   # Check database connectivity
   docker-compose exec bustapi python -c "
   import psycopg2
   conn = psycopg2.connect('postgresql://bustapi:password@db:5432/bustapi_db')
   print('Database connected successfully')
   "
   ```

3. **SSL Certificate Issues**
   ```bash
   # Check certificate
   openssl x509 -in /path/to/cert.pem -text -noout
   
   # Renew Let's Encrypt certificate
   certbot renew
   ```

### Performance Debugging

```bash
# Profile application
pip install py-spy
py-spy top --pid $(pgrep -f gunicorn)

# Load testing
pip install locust
locust -f locustfile.py --host=http://localhost:8000

# Monitor logs
docker-compose logs -f bustapi | grep ERROR
```

## 📚 Additional Resources

- [BustAPI Documentation](../../README.md)
- [Performance Benchmarks](../../benchmarks/README.md)
- [Security Guide](../docs/security.md)
- [API Reference](../docs/api-reference.md)

---

**BustAPI** - High-performance Python web framework powered by Rust 🚀
