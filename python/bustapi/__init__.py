"""
BustAPI - High-performance Flask-compatible web framework

BustAPI is a Flask-compatible Python web framework built with a Rust backend
using PyO3. It provides high performance while maintaining Flask's ease of use.

Example:
    from bustapi import BustAPI

    app = BustAPI()

    @app.route('/')
    def hello():
        return {'message': 'Hello, World!'}

    if __name__ == '__main__':
        app.run(debug=True)
"""

__version__ = "0.1.0"
__author__ = "BustAPI Team"
__email__ = "hello@bustapi.dev"

# Import core classes and functions
from .app import BustAPI
from .request import Request, request
from .response import Response, jsonify, make_response
from .helpers import abort, redirect, url_for
from .blueprints import Blueprint

# Import Flask compatibility helpers
from .flask_compat import Flask

# Import testing utilities
from .testing import TestClient

# Common HTTP status codes for convenience
from http import HTTPStatus

__all__ = [
    # Core classes
    'BustAPI',
    'Request',
    'Response', 
    'Blueprint',
    'TestClient',
    
    # Global objects
    'request',
    
    # Helper functions
    'jsonify',
    'make_response',
    'abort',
    'redirect',
    'url_for',
    
    # Flask compatibility
    'Flask',
    
    # HTTP status codes
    'HTTPStatus',
    
    # Version info
    '__version__',
]

# Convenience imports for common use cases
try:
    from .extensions.cors import CORS
    __all__.append('CORS')
except ImportError:
    pass

def get_version():
    """Get the current version of BustAPI."""
    return __version__

def get_debug_info():
    """Get debug information about the current BustAPI installation."""
    import sys
    import platform
    
    try:
        from . import bustapi_core
        rust_version = getattr(bustapi_core, '__version__', 'unknown')
    except ImportError:
        rust_version = 'not available'
    
    return {
        'bustapi_version': __version__,
        'rust_core_version': rust_version,
        'python_version': sys.version,
        'platform': platform.platform(),
        'architecture': platform.architecture(),
    }

# Set up default logging
import logging
logging.getLogger('bustapi').addHandler(logging.NullHandler())