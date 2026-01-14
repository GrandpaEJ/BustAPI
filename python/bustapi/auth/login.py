"""
Login management for session-based authentication.

Flask-Login style API for managing user sessions.
"""

from functools import wraps
from typing import Any, Callable, Optional, Union

from ..utils import LocalProxy
from .user import AnonUser


class LoginManager:
    """
    Manages user session authentication.

    Usage:
        login_manager = LoginManager(app)

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(user_id)
    """

    def __init__(self, app=None):
        self._app = None
        self._user_loader_callback = None
        self._anonymous_user = AnonUser

        # Session config
        self.session_key = "_user_id"
        self.remember_key = "_remember"
        self.fresh_key = "_fresh"
        self.login_view = None
        self.login_message = "Please log in to access this page."

        if app is not None:
            self.init_app(app)

    def init_app(self, app) -> None:
        """Initialize with application."""
        self._app = app
        app.extensions["login_manager"] = self

        # Store reference for current_user proxy
        app.login_manager = self

        # Register request hooks
        app.before_request(self._load_user)

    def user_loader(self, callback: Callable[[str], Any]) -> Callable:
        """
        Decorator to register user loader function.

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(user_id)
        """
        self._user_loader_callback = callback
        return callback

    def _load_user(self) -> None:
        """Load user from session on each request."""
        from ..http.request import request, session

        # Default to anonymous
        request._login_user = self._anonymous_user()

        if not session:
            return

        user_id = session.get(self.session_key)
        if user_id is None:
            return

        if self._user_loader_callback is None:
            return

        # Load user via callback
        user = self._user_loader_callback(user_id)
        if user is not None:
            request._login_user = user
            request._login_fresh = session.get(self.fresh_key, False)


def login_user(user, remember: bool = False, fresh: bool = True) -> bool:
    """
    Log in a user.

    Args:
        user: User object (must have get_id() method)
        remember: Create persistent session
        fresh: Mark session as fresh (from password login)

    Returns:
        True if successful
    """
    from ..http.request import request, session

    if not session:
        return False

    # Get user ID
    user_id = getattr(user, "get_id", lambda: None)()
    if user_id is None:
        try:
            user_id = str(user.id)
        except AttributeError:
            return False

    # Get login manager config
    login_manager = getattr(request, "_app", None)
    if login_manager:
        login_manager = getattr(login_manager, "login_manager", None)

    session_key = "_user_id"
    fresh_key = "_fresh"
    remember_key = "_remember"

    if login_manager:
        session_key = login_manager.session_key
        fresh_key = login_manager.fresh_key
        remember_key = login_manager.remember_key

    # Set session
    session[session_key] = user_id
    session[fresh_key] = fresh
    session[remember_key] = remember

    # Update request
    request._login_user = user
    request._login_fresh = fresh

    return True


def logout_user() -> bool:
    """
    Log out current user.

    Returns:
        True if successful
    """
    from ..http.request import request, session

    if not session:
        return False

    # Get login manager config
    login_manager = getattr(request, "_app", None)
    if login_manager:
        login_manager = getattr(login_manager, "login_manager", None)

    session_key = "_user_id"
    fresh_key = "_fresh"
    remember_key = "_remember"

    if login_manager:
        session_key = login_manager.session_key
        fresh_key = login_manager.fresh_key
        remember_key = login_manager.remember_key

    # Clear session
    session.pop(session_key, None)
    session.pop(fresh_key, None)
    session.pop(remember_key, None)

    # Reset request user
    if login_manager:
        request._login_user = login_manager._anonymous_user()
    else:
        request._login_user = AnonUser()

    return True


def _get_user():
    """Get current user from request context."""
    from ..http.request import request

    if hasattr(request, "_login_user"):
        return request._login_user

    return AnonUser()


# Proxy to current user
current_user: Any = LocalProxy(_get_user)
