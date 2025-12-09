# app.py
from catzilla import (
    Catzilla, Request, Response, JSONResponse
)

# Initialize Catzilla
app = Catzilla(
    production=False,      # Enable development features
    show_banner=True,      # Show startup banner
    log_requests=True      # Log requests in development
)

# Basic sync route
@app.get("/")
def home(request: Request) -> Response:
    """Home endpoint - SYNC handler"""
    return JSONResponse({
        "message": "Welcome to Catzilla v0.2.0!",
        "framework": "Catzilla v0.2.0",
        "router": "C-Accelerated with Async Support",
        "handler_type": "sync"
    })

# Health check
@app.get("/health")
def health_check(request: Request) -> Response:
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "version": "0.2.0",
        "async_support": "enabled"
    })

if __name__ == "__main__":
    app.listen(port=8000, host="0.0.0.0")