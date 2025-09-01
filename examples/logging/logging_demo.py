#!/usr/bin/env python3
"""
BustAPI Enhanced Logging Demo

Demonstrates advanced logging features with execution time tracking,
smart time units (s, ms, μs, ns), and error handling.
"""

from bustapi import BustAPI, setup_logging, get_logger, request_logging_middleware
import time
import random

# Setup enhanced colorful logging
logger = setup_logging(level="DEBUG", use_colors=True)

app = BustAPI(
    title="Enhanced Logging Demo",
    version="1.0.0",
    description="Advanced logging with execution time tracking and smart time units"
)

# Create a custom logger for this demo
demo_logger = get_logger("enhanced_demo")

# Apply request logging middleware to specific routes
@request_logging_middleware(demo_logger)
@app.route('/')
def index():
    """Root endpoint with automatic request logging."""
    return {
        'message': 'Enhanced Logging Demo',
        'features': [
            'Execution time tracking',
            'Smart time units (s, ms, μs, ns)',
            'Automatic request logging',
            'Error tracking',
            'Colored output by performance'
        ]
    }

@request_logging_middleware(demo_logger)
@app.route('/api/ultra-fast')
def ultra_fast():
    """Ultra-fast endpoint (< 1ms) - should show in μs or ns."""
    # Simulate very fast processing
    time.sleep(0.0001)  # 100μs
    return {'speed': 'ultra-fast', 'time': '< 1ms'}

@request_logging_middleware(demo_logger)
@app.route('/api/fast')
def fast():
    """Fast endpoint (1-10ms) - should show in ms."""
    time.sleep(0.005)  # 5ms
    return {'speed': 'fast', 'time': '1-10ms'}

@request_logging_middleware(demo_logger)
@app.route('/api/normal')
def normal():
    """Normal endpoint (10-100ms) - should show in ms."""
    time.sleep(0.050)  # 50ms
    return {'speed': 'normal', 'time': '10-100ms'}

@request_logging_middleware(demo_logger)
@app.route('/api/slow')
def slow():
    """Slow endpoint (100-500ms) - should show in ms with yellow color."""
    time.sleep(0.300)  # 300ms
    return {'speed': 'slow', 'time': '100-500ms'}

@request_logging_middleware(demo_logger)
@app.route('/api/very-slow')
def very_slow():
    """Very slow endpoint (> 1s) - should show in s with red color."""
    time.sleep(1.2)  # 1.2s
    return {'speed': 'very-slow', 'time': '> 1s'}

@request_logging_middleware(demo_logger)
@app.route('/api/random-speed')
def random_speed():
    """Random speed endpoint to demonstrate different time units."""
    # Random delay between 0.1ms and 2s
    delay = random.uniform(0.0001, 2.0)
    time.sleep(delay)
    
    if delay < 0.001:
        speed_category = "ultra-fast"
    elif delay < 0.01:
        speed_category = "fast"
    elif delay < 0.1:
        speed_category = "normal"
    elif delay < 0.5:
        speed_category = "slow"
    else:
        speed_category = "very-slow"
    
    return {
        'speed': speed_category,
        'actual_delay': f"{delay:.6f}s",
        'message': 'Random speed demonstration'
    }

@request_logging_middleware(demo_logger)
@app.route('/api/error-demo')
def error_demo():
    """Endpoint that demonstrates error logging."""
    time.sleep(0.050)  # Some processing time
    
    # Simulate random errors
    error_type = random.choice(['database', 'network', 'validation', 'success'])
    
    if error_type == 'database':
        raise Exception("Database connection failed")
    elif error_type == 'network':
        raise Exception("Network timeout occurred")
    elif error_type == 'validation':
        raise Exception("Invalid input data")
    else:
        return {'status': 'success', 'message': 'No error this time!'}

@request_logging_middleware(demo_logger)
@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """User endpoint with parameter logging and different response codes."""
    # Simulate database lookup time
    time.sleep(random.uniform(0.010, 0.100))  # 10-100ms
    
    if user_id == 404:
        return {'error': 'User not found'}, 404
    elif user_id == 500:
        raise Exception("Internal server error while fetching user")
    elif user_id == 403:
        return {'error': 'Access forbidden'}, 403
    else:
        return {
            'user_id': user_id,
            'name': f'User {user_id}',
            'status': 'active',
            'created_at': '2024-01-01T00:00:00Z'
        }

@request_logging_middleware(demo_logger)
@app.route('/api/batch-process', methods=['POST'])
def batch_process():
    """Simulate batch processing with variable execution time."""
    # Simulate processing multiple items
    items = random.randint(1, 10)
    processing_time = items * 0.1  # 100ms per item
    
    time.sleep(processing_time)
    
    return {
        'processed_items': items,
        'processing_time': f"{processing_time:.3f}s",
        'status': 'completed'
    }

# Manual logging examples (without middleware)
@app.route('/api/manual-logging')
def manual_logging():
    """Demonstrate manual logging with custom timing."""
    start_time = time.perf_counter()
    
    # Simulate some work
    time.sleep(0.075)  # 75ms
    
    # Manual timing calculation
    duration = time.perf_counter() - start_time
    
    # Manual request logging
    demo_logger.log_request(
        method="GET",
        path="/api/manual-logging",
        status_code=200,
        duration=duration
    )
    
    return {
        'message': 'Manual logging example',
        'duration': f"{duration:.6f}s",
        'note': 'This was logged manually'
    }

@app.route('/api/manual-error')
def manual_error():
    """Demonstrate manual error logging."""
    start_time = time.perf_counter()
    
    try:
        # Simulate some work that fails
        time.sleep(0.030)  # 30ms
        raise ValueError("Simulated validation error")
        
    except Exception as e:
        duration = time.perf_counter() - start_time
        
        # Manual error logging
        demo_logger.log_request(
            method="GET",
            path="/api/manual-error",
            status_code=400,
            duration=duration,
            error=str(e)
        )
        
        return {'error': str(e)}, 400

if __name__ == '__main__':
    print("\n" + "="*70)
    print("⚡ BustAPI Enhanced Logging Demo")
    print("="*70)
    print("This demo shows advanced logging features:")
    print("• ⏱️  Execution time tracking with smart units:")
    print("  - 🟢 < 100ms = Green (fast)")
    print("  - 🔵 100ms-500ms = Cyan (ok)")  
    print("  - 🟡 500ms-1s = Yellow (slow)")
    print("  - 🔴 > 1s = Red (very slow)")
    print("• 📏 Smart time units: ns, μs, ms, s")
    print("• 🎯 Automatic request logging middleware")
    print("• ❌ Error tracking and logging")
    print("• 🌈 Color-coded by performance")
    print("\nEndpoints to test:")
    print("• GET  / - Root with basic info")
    print("• GET  /api/ultra-fast - < 1ms (μs/ns display)")
    print("• GET  /api/fast - ~5ms (green)")
    print("• GET  /api/normal - ~50ms (green)")
    print("• GET  /api/slow - ~300ms (yellow)")
    print("• GET  /api/very-slow - ~1.2s (red)")
    print("• GET  /api/random-speed - Random timing")
    print("• GET  /api/error-demo - Random errors")
    print("• GET  /api/users/123 - User found")
    print("• GET  /api/users/404 - User not found")
    print("• GET  /api/users/500 - Server error")
    print("• POST /api/batch-process - Variable timing")
    print("• GET  /api/manual-logging - Manual timing")
    print("• GET  /api/manual-error - Manual error logging")
    print("="*70)
    
    # Demo the logging system before starting
    demo_logger.info("🚀 Enhanced logging system initialized")
    demo_logger.debug("Debug mode enabled for demonstration")
    
    # Demo different time units
    print("\n📊 Time Unit Examples:")
    demo_logger.log_request("GET", "/demo/nanoseconds", 200, 0.000000123)   # 123ns
    demo_logger.log_request("GET", "/demo/microseconds", 200, 0.000456)     # 456μs  
    demo_logger.log_request("GET", "/demo/milliseconds", 200, 0.123)        # 123ms
    demo_logger.log_request("GET", "/demo/seconds", 200, 1.234)             # 1.234s
    
    print("\n🚦 Status Code Colors:")
    demo_logger.log_request("GET", "/demo/success", 200, 0.050)
    demo_logger.log_request("POST", "/demo/created", 201, 0.075)
    demo_logger.log_request("GET", "/demo/not-found", 404, 0.025)
    demo_logger.log_request("POST", "/demo/error", 500, 0.100, "Database error")
    
    print("\n🎯 Starting server with enhanced logging...")
    
    # Start server
    app.run(host='127.0.0.1', port=8000, debug=True)
