"""
CSRF protection middleware.
"""

from .tokens import generate_csrf_token


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

    def exempt(self, fn):
        """Mark a view as exempt from CSRF protection."""
        self._exempt_views.add(fn.__name__)
        return fn

    def _get_csrf_token(self) -> str:
        """Get or create CSRF token for current session."""
        from ..http.request import session

        if not session:
            return ""

        token = session.get("_csrf_token")
        if not token:
            token = generate_csrf_token()
            session["_csrf_token"] = token

        return token

    def _check_csrf(self) -> None:
        """Check CSRF token on state-changing requests."""
        from ..http.request import request, session

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
            from ..core.exceptions import abort

            abort(403, "CSRF token missing or invalid")
