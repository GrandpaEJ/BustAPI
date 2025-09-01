#!/usr/bin/env python3
"""
Simple BustAPI Logging Test

Test the simplified logging interface.
"""

from bustapi import BustAPI, logging

# Simple setup
logging.setup(level="DEBUG", use_colors=True)

app = BustAPI(title="Simple Logging Test")

@app.route('/')
def index():
    logging.info("Processing root request")
    return {'message': 'Simple logging test'}

@app.route('/api/test')
def test():
    logging.debug("Debug message for test endpoint")
    logging.info("Processing test request")
    return {'test': True}

@app.route('/api/warning')
def warning():
    logging.warning("This is a warning message")
    return {'status': 'warning'}

@app.route('/api/error')
def error_endpoint():
    logging.error("This is an error message")
    return {'status': 'error'}, 500

if __name__ == '__main__':
    print("🧪 Simple Logging Test")
    print("=" * 40)
    print("Usage: from bustapi import logging")
    print("• logging.setup() - Setup logging")
    print("• logging.info() - Info messages")
    print("• logging.debug() - Debug messages")
    print("• logging.warning() - Warning messages")
    print("• logging.error() - Error messages")
    print("• logging.request() - Request logging")
    print("=" * 40)
    
    # Test basic logging
    logging.info("🚀 Starting simple logging test")
    logging.debug("Debug mode enabled")
    logging.warning("⚠️ This is a test warning")
    
    # Test request logging
    logging.request("GET", "/test", 200, 0.045)
    logging.request("POST", "/api/data", 201, 0.123)
    logging.request("GET", "/error", 500, 0.089, "Test error")
    
    print("\n🎯 Starting server...")
    app.run(host='127.0.0.1', port=8000, debug=True)
