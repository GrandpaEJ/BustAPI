import time
from typing import Dict, List, Optional, Tuple, Union

from ..http.request import Request
from ..http.response import Response


class RateLimit:
    """Simple in-memory rate limiter."""

    def __init__(self, limit: int, period: int = 60):
        """
        Args:
            limit: Number of requests allowed
            period: Time period in seconds
        """
        self.limit = limit
        self.period = period
        self.requests: Dict[str, List[float]] = {}

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for the given key (IP)."""
        now = time.time()
        if key not in self.requests:
            self.requests[key] = []

        # Filter out old requests
        self.requests[key] = [t for t in self.requests[key] if now - t < self.period]

        if len(self.requests[key]) >= self.limit:
            return False

        self.requests[key].append(now)
        return True


class Security:
    """
    Security extension for BustAPI.
    Provides CORS, Secure Headers, and Rate Limiting.
    """

    def __init__(self, app=None):
        self.app = None
        self._cors_enabled = False
        self._cors_origins = "*"
        self._cors_methods = [
            "GET",
            "HEAD",
            "POST",
            "OPTIONS",
            "PUT",
            "PATCH",
            "DELETE",
        ]
        self._cors_headers = ["Content-Type", "Authorization"]

        self._secure_headers_enabled = False
        self._hsts_enabled = False

        self._rate_limiter: Optional[RateLimit] = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize with application instance."""
        self.app = app
        app.extensions["security"] = self

        # Register hooks
        app.after_request(self._apply_security_headers)
        app.before_request(self._check_rate_limit)

    def enable_cors(
        self,
        origins: Union[str, List[str]] = "*",
        methods: Optional[List[str]] = None,
        allow_headers: Optional[List[str]] = None,
    ):
        """Enable CORS support."""
        self._cors_enabled = True
        self._cors_origins = origins
        if methods:
            self._cors_methods = methods
        if allow_headers:
            self._cors_headers = allow_headers

    def enable_secure_headers(self, hsts: bool = True):
        """Enable security headers (X-Frame-Options, X-XSS-Protection, etc.)."""
        self._secure_headers_enabled = True
        self._hsts_enabled = hsts

    def limit_requests(self, limit: int, period: int = 60):
        """Enable global rate limiting."""
        self._rate_limiter = RateLimit(limit, period)

    def _apply_security_headers(self, response: Response) -> Response:
        """Apply configured security headers to response."""
        if not response:
            return response

        # CORS
        if self._cors_enabled:
            # Origin
            if isinstance(self._cors_origins, str):
                allow_origin = self._cors_origins
            else:
                # Naive implementation: just return * or the first one for now
                # Real impl would check Origin request header
                allow_origin = ", ".join(self._cors_origins)

            response.headers["Access-Control-Allow-Origin"] = allow_origin
            response.headers["Access-Control-Allow-Methods"] = ", ".join(
                self._cors_methods
            )
            response.headers["Access-Control-Allow-Headers"] = ", ".join(
                self._cors_headers
            )

        # Secure Headers
        if self._secure_headers_enabled:
            response.headers.setdefault("X-Content-Type-Options", "nosniff")
            response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
            response.headers.setdefault("X-XSS-Protection", "1; mode=block")

            if self._hsts_enabled:
                response.headers.setdefault(
                    "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
                )

        return response

    def _check_rate_limit(self):
        """Check rate limit on incoming request."""
        if not self._rate_limiter:
            return

        # Need to access current request
        from ..http.request import request

        # Get client IP - naive implementation
        # In production this should handle X-Forwarded-For properly
        client_ip = "unknown"
        # We don't have direct access to remote_addr on Request yet, but let's assume valid request
        if request:
            # Use a dummy key if we can't get IP yet, or maybe just "global" for now if IP is missing
            client_ip = "global_user"

        if not self._rate_limiter.is_allowed(client_ip):
            from ..core.exceptions import abort

            abort(429, "Too Many Requests")
