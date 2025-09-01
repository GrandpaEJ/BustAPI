#!/usr/bin/env python3
"""
BustAPI Production Application

Production-ready BustAPI application with security, monitoring, and best practices.
"""

import logging
import os
import time

from bustapi import BustAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Configuration
class Config:
    """Application configuration."""

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # API Configuration
    API_TITLE = os.getenv("API_TITLE", "BustAPI Production")
    API_VERSION = os.getenv("API_VERSION", "1.0.0")
    API_DESCRIPTION = os.getenv("API_DESCRIPTION", "Production BustAPI application")


config = Config()

# Create BustAPI application
app = BustAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description=config.API_DESCRIPTION,
    # Disable docs in production for security
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None,
    openapi_url="/openapi.json" if config.DEBUG else None,
)


# Security middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # HSTS in production
    if config.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests for monitoring."""
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    # Add timing header
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Health check endpoint
@app.route("/health")
def health_check():
    """Comprehensive health check endpoint."""
    try:
        # Basic health check
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "version": config.API_VERSION,
            "environment": config.ENVIRONMENT,
        }

        # Add system information if available
        try:
            import psutil

            health_data["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
            }
        except ImportError:
            pass

        return health_data

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e), "timestamp": time.time()}, 503


# Readiness check (for Kubernetes)
@app.route("/ready")
def readiness_check():
    """Readiness check for container orchestration."""
    try:
        # Check database connection
        # db_healthy = check_database_connection()

        # Check Redis connection
        # redis_healthy = check_redis_connection()

        # For now, just return ready
        return {
            "status": "ready",
            "timestamp": time.time(),
            "checks": {
                "database": "ok",  # db_healthy
                "cache": "ok",  # redis_healthy
            },
        }

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not_ready", "error": str(e), "timestamp": time.time()}, 503


# Liveness check (for Kubernetes)
@app.route("/live")
def liveness_check():
    """Liveness check for container orchestration."""
    return {
        "status": "alive",
        "timestamp": time.time(),
        "uptime": time.time() - start_time,
    }


# Metrics endpoint (Prometheus compatible)
@app.route("/metrics")
def metrics():
    """Prometheus-compatible metrics endpoint."""
    try:
        # Basic metrics
        metrics_data = [
            "# HELP bustapi_info Application information",
            "# TYPE bustapi_info gauge",
            f'bustapi_info{{version="{config.API_VERSION}",environment="{config.ENVIRONMENT}"}} 1',
            "",
            "# HELP bustapi_uptime_seconds Application uptime in seconds",
            "# TYPE bustapi_uptime_seconds counter",
            f"bustapi_uptime_seconds {time.time() - start_time}",
        ]

        # Add system metrics if available
        try:
            import psutil

            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()

            metrics_data.extend(
                [
                    "",
                    "# HELP bustapi_cpu_percent CPU usage percentage",
                    "# TYPE bustapi_cpu_percent gauge",
                    f"bustapi_cpu_percent {cpu_percent}",
                    "",
                    "# HELP bustapi_memory_percent Memory usage percentage",
                    "# TYPE bustapi_memory_percent gauge",
                    f"bustapi_memory_percent {memory.percent}",
                ]
            )
        except ImportError:
            pass

        return "\n".join(metrics_data), 200, {"Content-Type": "text/plain"}

    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        return f"# Error generating metrics: {e}", 500, {"Content-Type": "text/plain"}


# API endpoints
@app.route("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": config.API_TITLE,
        "version": config.API_VERSION,
        "description": config.API_DESCRIPTION,
        "environment": config.ENVIRONMENT,
        "status": "running",
        "timestamp": time.time(),
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "live": "/live",
            "metrics": "/metrics",
            "docs": "/docs" if config.DEBUG else None,
        },
    }


@app.route("/api/v1/status")
def api_status():
    """API status endpoint."""
    return {
        "api_version": "v1",
        "status": "operational",
        "timestamp": time.time(),
        "features": {
            "authentication": False,  # Enable when implemented
            "rate_limiting": False,  # Enable when implemented
            "caching": False,  # Enable when implemented
        },
    }


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return {
        "error": "Not Found",
        "message": "The requested resource was not found",
        "status_code": 404,
        "timestamp": time.time(),
    }, 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return {
        "error": "Internal Server Error",
        "message": "An internal server error occurred",
        "status_code": 500,
        "timestamp": time.time(),
    }, 500


# Application startup
start_time = time.time()


def create_app():
    """Application factory."""
    logger.info(f"Starting {config.API_TITLE} v{config.API_VERSION}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"Debug mode: {config.DEBUG}")

    return app


if __name__ == "__main__":
    # Development server (not for production)
    if config.DEBUG:
        logger.warning("Running in debug mode - not suitable for production!")
        app.run(host="127.0.0.1", port=8000, debug=True)
    else:
        logger.error("Use a WSGI server like Gunicorn for production deployment")
        logger.info("Example: gunicorn -c gunicorn.conf.py production_app:app")
