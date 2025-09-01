#!/usr/bin/env python3
"""
BustAPI Colorful Logging Demo

Demonstrates BustAPI's smart colorful logging features.
"""

from bustapi import BustAPI, setup_logging, get_logger, log_info, log_debug, log_warning, log_error
import time

# Setup colorful logging
logger = setup_logging(level="DEBUG", use_colors=True)

app = BustAPI(
    title="Colorful Logging Demo",
    version="1.0.0",
    description="Demonstration of BustAPI's colorful logging features"
)

# Create a custom logger for this module
demo_logger = get_logger("demo")

@app.route('/')
def index():
    """Root endpoint with logging demo."""
    log_info("Processing root request")
    return {
        'message': 'Colorful Logging Demo',
        'features': [
            'Colored log levels',
            'HTTP request logging',
            'Smart status code colors',
            'Performance timing',
            'FastAPI-style output'
        ]
    }

@app.route('/api/success')
def success():
    """Successful API endpoint."""
    log_info("Successful API call")
    return {'status': 'success', 'code': 200}

@app.route('/api/warning')
def warning():
    """API endpoint that logs warnings."""
    log_warning("This endpoint generates a warning")
    return {'status': 'warning', 'message': 'Something might be wrong'}

@app.route('/api/error')
def error():
    """API endpoint that logs errors."""
    log_error("This endpoint generates an error log")
    return {'status': 'error', 'message': 'Something went wrong'}, 500

@app.route('/api/slow')
def slow():
    """Slow endpoint to demonstrate timing colors."""
    log_info("Processing slow request...")
    time.sleep(1)  # Simulate slow processing
    log_info("Slow request completed")
    return {'status': 'completed', 'duration': '1 second'}

@app.route('/api/debug')
def debug():
    """Endpoint with debug logging."""
    log_debug("Debug information for this endpoint")
    log_info("Processing debug endpoint")
    return {'debug': True, 'timestamp': time.time()}

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """User endpoint with parameter logging."""
    demo_logger.info(f"Fetching user {user_id}")
    
    if user_id == 404:
        demo_logger.warning(f"User {user_id} not found")
        return {'error': 'User not found'}, 404
    
    demo_logger.info(f"User {user_id} found successfully")
    return {
        'user_id': user_id,
        'name': f'User {user_id}',
        'status': 'active'
    }

@app.route('/api/test-methods', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def test_methods():
    """Test different HTTP methods for colored logging."""
    from bustapi import request
    method = request.method
    
    demo_logger.info(f"Received {method} request")
    
    return {
        'method': method,
        'message': f'Processed {method} request successfully'
    }

# Note: Middleware will be added in future versions
# For now, we'll demonstrate logging within route handlers

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎨 BustAPI Colorful Logging Demo")
    print("="*60)
    print("This demo shows BustAPI's colorful logging features:")
    print("• 🔵 Blue timestamps")
    print("• 🟢 Green INFO messages")
    print("• 🟡 Yellow WARNING messages") 
    print("• 🔴 Red ERROR messages")
    print("• 🎯 Colored HTTP methods (GET=Blue, POST=Green, etc.)")
    print("• 🚦 Status code colors (2xx=Green, 4xx=Red, 5xx=Magenta)")
    print("• ⏱️ Response time colors (Fast=Green, Slow=Red)")
    print("• 🚀 Special startup/shutdown messages")
    print("\nTry these endpoints:")
    print("• GET  / - Root with basic logging")
    print("• GET  /api/success - Success logging")
    print("• GET  /api/warning - Warning logging")
    print("• GET  /api/error - Error logging")
    print("• GET  /api/slow - Slow request (1s delay)")
    print("• GET  /api/debug - Debug logging")
    print("• GET  /api/users/123 - User found")
    print("• GET  /api/users/404 - User not found")
    print("• POST /api/test-methods - Test different methods")
    print("="*60)
    
    # Demo some logging before starting server
    log_info("🎨 Colorful logging initialized")
    log_debug("Debug mode enabled for demonstration")
    log_warning("⚠️ This is a demo warning message")
    
    # Start server with colorful logging
    app.run(host='127.0.0.1', port=8000, debug=True)
