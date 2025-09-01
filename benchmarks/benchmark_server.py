#!/usr/bin/env python3
"""
BustAPI Benchmark Server

Simple server for performance benchmarking.
"""

from bustapi import BustAPI, jsonify
import time
import json

app = BustAPI(
    title="BustAPI Benchmark Server",
    version="1.0.0",
    description="High-performance server for benchmarking"
)

# Simple in-memory data
users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
]

@app.route('/')
def root():
    """Simple root endpoint."""
    return {
        'message': 'BustAPI Benchmark Server',
        'version': '1.0.0',
        'timestamp': time.time(),
        'status': 'running'
    }

@app.route('/api/test')
def api_test():
    """Simple API test endpoint."""
    return {
        'test': True,
        'framework': 'BustAPI',
        'performance': 'high',
        'timestamp': time.time()
    }

@app.route('/api/users')
def get_users():
    """Get all users."""
    return {
        'users': users,
        'count': len(users),
        'timestamp': time.time()
    }

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """Get user by ID."""
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        return {
            'user': user,
            'timestamp': time.time()
        }
    return {'error': 'User not found'}, 404

@app.route('/api/health')
def health():
    """Health check endpoint."""
    return {
        'status': 'healthy',
        'uptime': time.time(),
        'framework': 'BustAPI',
        'version': '1.0.0'
    }

@app.route('/api/echo', methods=['POST'])
def echo():
    """Echo endpoint for POST testing."""
    try:
        from bustapi import request
        data = request.get_json() or {}
        return {
            'echo': data,
            'method': 'POST',
            'timestamp': time.time()
        }
    except:
        return {
            'echo': 'No JSON data',
            'method': 'POST',
            'timestamp': time.time()
        }

@app.route('/api/compute')
def compute():
    """CPU-intensive endpoint for testing."""
    # Simple computation to simulate work
    result = sum(i * i for i in range(1000))
    return {
        'computation': result,
        'iterations': 1000,
        'timestamp': time.time()
    }

@app.route('/api/large')
def large_response():
    """Large response for testing."""
    data = {
        'message': 'Large response test',
        'data': [
            {
                'id': i,
                'name': f'Item {i}',
                'description': f'This is item number {i} with some description text',
                'value': i * 10,
                'active': i % 2 == 0
            }
            for i in range(100)
        ],
        'timestamp': time.time(),
        'count': 100
    }
    return data

if __name__ == '__main__':
    print("🚀 Starting BustAPI Benchmark Server...")
    print("📍 Server: http://127.0.0.1:8000")
    print("📊 Endpoints:")
    print("   GET  / - Root endpoint")
    print("   GET  /api/test - Simple test")
    print("   GET  /api/users - Get users")
    print("   GET  /api/users/{id} - Get user by ID")
    print("   GET  /api/health - Health check")
    print("   POST /api/echo - Echo POST data")
    print("   GET  /api/compute - CPU-intensive")
    print("   GET  /api/large - Large response")
    print("\n💡 Use benchmarks/comprehensive_benchmark.py to test performance")
    
    app.run(host='127.0.0.1', port=8000, debug=False)
