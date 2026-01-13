"""
BustAPI Auth Extension

Authentication utilities including:
- Password hashing (Argon2id via Rust)
- Login decorators
- CSRF protection
"""

from functools import wraps
from typing import Callable, Optional

from .bustapi_core import (
    generate_csrf_token,
    generate_token,
    hash_password,
    verify_password,
)
from .http.request import request, session

# Re-export Rust functions
__all__ = [
    "hash_password",
    "verify_password",
    "generate_token",
    "generate_csrf_token",
    "login_required",
    "current_user",
    "CSRFProtect",
]


def login_required(fn: Callable) -> Callable:
    """
    Decorator to require user to be logged in (session-based).

    Checks for 'user_id' or 'logged_in' in session.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Check session for login status
        if not session:
            from .core.exceptions import abort

            abort(401, "Login required")

        user_id = session.get("user_id") or session.get("user")
        logged_in = session.get("logged_in", False)

        if not user_id and not logged_in:
            from .core.exceptions import abort

            abort(401, "Login required")

        # Set current user on request
        request.current_user_id = user_id

        return fn(*args, **kwargs)

    return wrapper


def current_user() -> Optional[str]:
    """
    Get the current authenticated user ID.

    Returns:
        User ID from session, or None if not logged in
    """
    if not session:
        return None

    return session.get("user_id") or session.get("user")


class CSRFProtect:
    """
    CSRF protection extension.

    Usage:
        csrf = CSRFProtect(app)

        @app.post("/submit")
        def submit():
            # CSRF token automatically validated
            ...

        # In template:
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    """

    def __init__(self, app=None):
        self._app = None
        self._exempt_views = set()

        if app is not None:
            self.init_app(app)

    def init_app(self, app) -> None:
        """Initialize with application instance."""
        self._app = app
        app.extensions["csrf"] = self

        # Register before_request hook
        app.before_request(self._check_csrf)

        # Add csrf_token to template context
        @app.context_processor
        def csrf_context():
            return {"csrf_token": self._get_csrf_token}

    def exempt(self, fn: Callable) -> Callable:
        """Mark a view as exempt from CSRF protection."""
        self._exempt_views.add(fn.__name__)
        return fn

    def _get_csrf_token(self) -> str:
        """Get or create CSRF token for current session."""
        if not session:
            return ""

        token = session.get("_csrf_token")
        if not token:
            token = generate_csrf_token()
            session["_csrf_token"] = token

        return token

    def _check_csrf(self) -> None:
        """Check CSRF token on state-changing requests."""
        if not request:
            return

        # Only check on state-changing methods
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return

        # Check if exempt
        endpoint = getattr(request, "endpoint", None)
        if endpoint and endpoint in self._exempt_views:
            return

        # Get expected token from session
        expected = session.get("_csrf_token") if session else None
        if not expected:
            return  # No CSRF token set, skip check

        # Get submitted token
        submitted = None

        # Check form data
        if request.form:
            submitted = request.form.get("csrf_token") or request.form.get(
                "_csrf_token"
            )

        # Check header
        if not submitted:
            submitted = request.headers.get("X-CSRF-Token") or request.headers.get(
                "X-CSRFToken"
            )

        if not submitted or submitted != expected:
            from .core.exceptions import abort

            abort(403, "CSRF token missing or invalid")
