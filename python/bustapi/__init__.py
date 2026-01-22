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

__version__ = "0.9.0"
__author__ = "BustAPI"
__email__ = ""

# Import core modules
# Import core classes and functions
from . import logging
from .app import BustAPI
from .auth import (
    AnonUser,
    # User Classes
    BaseUser,
    # CSRF
    CSRFProtect,
    # Login Management
    LoginManager,
    current_user,
    fresh_login_required,
    generate_csrf_token,
    # Tokens
    generate_token,
    # Password
    hash_password,
    # Decorators
    login_required,
    login_user,
    logout_user,
    permission_required,
    roles_required,
    verify_password,
)
from .core.helpers import abort, redirect, render_template, send_file, url_for
from .dependencies import Depends
from .documentation.generator import BustAPIDocs
from .fastapi_compat import (
    BackgroundTasks,
    Cookie,
    File,
    Form,
    Header,
    UploadFile,
)
from .http.request import Request, current_app, g, request, session
from .http.response import Response, jsonify, make_response

# JWT and Auth
from .jwt import (
    JWT,
    fresh_jwt_required,
    jwt_optional,
    jwt_refresh_token_required,
    jwt_required,
)
from .middleware import Middleware
from .params import Body, Path, Query
from .responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    StreamingResponse,
)
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
    "logging",
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
    "Header",
    "Cookie",
    "Form",
    "File",
    "UploadFile",
    "BackgroundTasks",
    "Struct",
    "String",
    "Integer",
    "HTTPStatus",
    "__version__",
    "JSONResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "RedirectResponse",
    "FileResponse",
    "StreamingResponse",
    # JWT
    "JWT",
    "jwt_required",
    "jwt_optional",
    "fresh_jwt_required",
    "jwt_refresh_token_required",
    # Auth - Login
    "LoginManager",
    "login_user",
    "logout_user",
    "current_user",
    # Auth - User Classes
    "BaseUser",
    "AnonUser",
    # Auth - Decorators
    "login_required",
    "fresh_login_required",
    "roles_required",
    "permission_required",
    # Auth - Password
    "hash_password",
    "verify_password",
    # Auth - Tokens
    "generate_token",
    "generate_csrf_token",
    # Auth - CSRF
    "CSRFProtect",
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
