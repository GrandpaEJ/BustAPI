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

import logging as _logging
import platform
import sys
from http import HTTPStatus

__version__ = "0.4.0"
__author__ = "BustAPI"
__email__ = ""

# Import core modules
# Import core classes and functions
from .app import BustAPI
from .core import logging
from .core.helpers import abort, redirect, render_template, url_for
from .dependencies import Depends
from .documentation.generator import BustAPIDocs
from .http.request import Request, request, session
from .http.response import Response, jsonify, make_response
from .middleware import Middleware
from .params import Body, Path, Query
from .routing.blueprints import Blueprint
from .security.extension import Security
from .security.rate_limit import RateLimit

# Import testing utilities
from .testing.client import TestClient

__all__ = [
    "BustAPI",
    "Request",
    "Response",
    "make_response",
    "jsonify",
    "redirect",
    "send_file",
    "abort",
    "Blueprint",
    "Path",
    "Query",
    "Body",
    "Depends",
    "render_template",
    "render_template_string",
    "url_for",
    "flash",
    "get_flashed_messages",
    "session",
    "request",
    "g",
    "current_app",
    "Middleware",
    "RateLimiter",
    "TestClient",
    "Struct",
    "String",
    "Integer",
    "HTTPStatus",
    "__version__",
]

# Convenience imports for common use cases
try:
    from .extensions.cors import CORS  # noqa: F401

    __all__.append("CORS")
except ImportError:
    pass


def get_version():
    """Get the current version of BustAPI."""
    return __version__


def get_debug_info():
    """Get debug information about the current BustAPI installation."""
    try:
        from . import bustapi_core

        rust_version = getattr(bustapi_core, "__version__", "unknown")
    except ImportError:
        rust_version = "not available"

    return {
        "bustapi_version": __version__,
        "rust_core_version": rust_version,
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture(),
    }


# Set up default logging
_logging.getLogger("bustapi").addHandler(_logging.NullHandler())
