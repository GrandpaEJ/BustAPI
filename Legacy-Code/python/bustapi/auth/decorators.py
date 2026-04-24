"""
Authentication decorators for route protection.
"""

from functools import wraps
from typing import Callable, Iterable, Optional, Union


def login_required(fn: Callable) -> Callable:
    """
    Require authenticated user to access route.

    Usage:
        @app.get("/dashboard")
        @login_required
        def dashboard():
            return f"Hello, {current_user.name}!"
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        from ..core.exceptions import abort
        from .login import current_user

        if not current_user.is_authenticated:
            # Get login manager for redirect config
            from ..http.request import request

            login_manager = getattr(
                getattr(request, "_app", None), "login_manager", None
            )

            if login_manager and login_manager.login_view:
                from ..core.helpers import redirect, url_for

                return redirect(url_for(login_manager.login_view))

            abort(401, "Login required")

        return fn(*args, **kwargs)

    return wrapper


def fresh_login_required(fn: Callable) -> Callable:
    """
    Require fresh login (from password, not remember-me).

    Use for sensitive operations like password change.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        from ..core.exceptions import abort
        from ..http.request import request
        from .login import current_user

        if not current_user.is_authenticated:
            abort(401, "Login required")

        if not getattr(request, "_login_fresh", False):
            abort(401, "Fresh login required")

        return fn(*args, **kwargs)

    return wrapper


def roles_required(*roles: str) -> Callable:
    """
    Require user to have specific role(s).

    Usage:
        @app.get("/admin")
        @roles_required("admin")
        def admin_panel():
            ...

        @app.get("/moderator")
        @roles_required("admin", "moderator")
        def mod_panel():
            ...
    """

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from ..core.exceptions import abort
            from .login import current_user

            if not current_user.is_authenticated:
                abort(401, "Login required")

            # Get user roles
            user_roles = getattr(current_user, "roles", None)
            if user_roles is None:
                user_roles = getattr(current_user, "role", None)
                if user_roles is not None:
                    user_roles = [user_roles]
                else:
                    user_roles = []

            # Check if user has any required role
            if not any(r in user_roles for r in roles):
                abort(403, f"Role required: {', '.join(roles)}")

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def permission_required(*permissions: str) -> Callable:
    """
    Require user to have specific permission(s).

    Usage:
        @app.post("/delete")
        @permission_required("delete_posts")
        def delete_post():
            ...
    """

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from ..core.exceptions import abort
            from .login import current_user

            if not current_user.is_authenticated:
                abort(401, "Login required")

            # Get user permissions
            user_perms = getattr(current_user, "permissions", [])
            if callable(user_perms):
                user_perms = user_perms()

            # Check all required permissions
            for perm in permissions:
                if perm not in user_perms:
                    abort(403, f"Permission required: {perm}")

            return fn(*args, **kwargs)

        return wrapper

    return decorator
