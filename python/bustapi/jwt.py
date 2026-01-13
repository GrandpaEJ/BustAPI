"""
BustAPI JWT Extension

High-performance JWT support with Rust backend.

Example:
    from bustapi import BustAPI, JWT, jwt_required

    app = BustAPI(__name__)
    jwt = JWT(app, secret_key="your-secret-key")

    @app.post("/login")
    def login(username: str, password: str):
        token = jwt.create_access_token(identity=user_id)
        return {"access_token": token}

    @app.get("/protected")
    @jwt_required
    def protected(request):
        return {"user": request.jwt_identity}
"""

from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

from .http.request import request


class JWT:
    """
    JWT extension for BustAPI.

    Provides JWT-based authentication with Rust-backed encoding/decoding.
    """

    def __init__(
        self,
        app=None,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_expires: int = 900,  # 15 minutes
        refresh_expires: int = 2592000,  # 30 days
    ):
        """
        Initialize JWT extension.

        Args:
            app: BustAPI application instance
            secret_key: Secret key for signing tokens (uses app.secret_key if not provided)
            algorithm: Algorithm to use (HS256, HS384, HS512)
            access_expires: Access token expiry in seconds (default: 15 min)
            refresh_expires: Refresh token expiry in seconds (default: 30 days)
        """
        self._app = None
        self._manager = None
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expires = access_expires
        self._refresh_expires = refresh_expires

        if app is not None:
            self.init_app(app)

    def init_app(self, app) -> None:
        """Initialize with application instance."""
        from .bustapi_core import JWTManager

        self._app = app
        app.extensions["jwt"] = self

        # Use provided secret or app's secret
        secret = self._secret_key or app.secret_key
        if not secret:
            raise ValueError(
                "JWT requires a secret key. Set app.secret_key or pass secret_key to JWT()"
            )

        self._manager = JWTManager(
            secret,
            self._algorithm,
            self._access_expires,
            self._refresh_expires,
        )

    def create_access_token(
        self,
        identity: Union[str, int],
        expires_delta: Optional[int] = None,
        fresh: bool = True,
        claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create an access token.

        Args:
            identity: User identity (usually user ID)
            expires_delta: Custom expiry in seconds (optional)
            fresh: Whether token is fresh (from login, not refresh)
            claims: Additional claims to include

        Returns:
            JWT token string
        """
        if self._manager is None:
            raise RuntimeError("JWT not initialized. Call init_app() first.")

        return self._manager.create_access_token(
            str(identity), expires_delta, fresh, claims
        )

    def create_refresh_token(
        self,
        identity: Union[str, int],
        expires_delta: Optional[int] = None,
        claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a refresh token.

        Args:
            identity: User identity (usually user ID)
            expires_delta: Custom expiry in seconds (optional)
            claims: Additional claims to include

        Returns:
            JWT token string
        """
        if self._manager is None:
            raise RuntimeError("JWT not initialized. Call init_app() first.")

        return self._manager.create_refresh_token(str(identity), expires_delta, claims)

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and verify a token.

        Args:
            token: JWT token string

        Returns:
            Dict with token claims

        Raises:
            ValueError: If token is invalid or expired
        """
        if self._manager is None:
            raise RuntimeError("JWT not initialized. Call init_app() first.")

        return self._manager.decode_token(token)

    def verify_token(self, token: str) -> bool:
        """
        Verify a token without decoding.

        Returns:
            True if valid, False otherwise
        """
        if self._manager is None:
            return False

        return self._manager.verify_token(token)

    def get_identity(self, token: str) -> Optional[str]:
        """
        Get identity from token (works even on expired tokens).

        Returns:
            Identity string or None
        """
        if self._manager is None:
            return None

        return self._manager.get_identity(token)


# Global JWT instance for decorators
_jwt_instance: Optional[JWT] = None


def _get_jwt() -> JWT:
    """Get the global JWT instance."""
    global _jwt_instance

    if _jwt_instance is not None:
        return _jwt_instance

    # Try to get from current app
    if request and hasattr(request, "_app") and request._app:
        jwt_ext = request._app.extensions.get("jwt")
        if jwt_ext:
            return jwt_ext

    raise RuntimeError("No JWT instance found. Initialize JWT(app) first.")


def _get_token_from_request() -> Optional[str]:
    """Extract JWT from Authorization header."""
    auth_header = request.headers.get("Authorization", "")

    if auth_header.startswith("Bearer "):
        return auth_header[7:]

    return None


def jwt_required(fn: Callable) -> Callable:
    """
    Decorator to require a valid JWT token.

    Token must be in Authorization header as: Bearer <token>

    Sets request.jwt_identity and request.jwt_claims.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _get_token_from_request()

        if not token:
            from .core.exceptions import abort

            abort(401, "Missing Authorization header")

        try:
            jwt_ext = _get_jwt()
            claims = jwt_ext.decode_token(token)

            # Set on request context
            request.jwt_identity = claims.get("identity")
            request.jwt_claims = claims

        except ValueError as e:
            from .core.exceptions import abort

            abort(401, str(e))

        return fn(*args, **kwargs)

    return wrapper


def jwt_optional(fn: Callable) -> Callable:
    """
    Decorator for optional JWT.

    If valid token present, sets request.jwt_identity and request.jwt_claims.
    If not, sets them to None and continues.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _get_token_from_request()

        request.jwt_identity = None
        request.jwt_claims = None

        if token:
            try:
                jwt_ext = _get_jwt()
                claims = jwt_ext.decode_token(token)
                request.jwt_identity = claims.get("identity")
                request.jwt_claims = claims
            except ValueError:
                pass  # Invalid token, but optional

        return fn(*args, **kwargs)

    return wrapper


def fresh_jwt_required(fn: Callable) -> Callable:
    """
    Decorator to require a fresh JWT token.

    Fresh tokens are created from login, not from refresh.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _get_token_from_request()

        if not token:
            from .core.exceptions import abort

            abort(401, "Missing Authorization header")

        try:
            jwt_ext = _get_jwt()
            claims = jwt_ext.decode_token(token)

            if not claims.get("fresh", False):
                from .core.exceptions import abort

                abort(401, "Fresh token required")

            request.jwt_identity = claims.get("identity")
            request.jwt_claims = claims

        except ValueError as e:
            from .core.exceptions import abort

            abort(401, str(e))

        return fn(*args, **kwargs)

    return wrapper


def jwt_refresh_token_required(fn: Callable) -> Callable:
    """
    Decorator to require a refresh token.

    Used for the token refresh endpoint.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _get_token_from_request()

        if not token:
            from .core.exceptions import abort

            abort(401, "Missing Authorization header")

        try:
            jwt_ext = _get_jwt()
            claims = jwt_ext.decode_token(token)

            if claims.get("type") != "refresh":
                from .core.exceptions import abort

                abort(401, "Refresh token required")

            request.jwt_identity = claims.get("identity")
            request.jwt_claims = claims

        except ValueError as e:
            from .core.exceptions import abort

            abort(401, str(e))

        return fn(*args, **kwargs)

    return wrapper
