from functools import wraps
from typing import Optional, Tuple

from ..core.exceptions import abort


class RateLimit:
    """
    Rate limiting extension using high-performance Rust backend.

    Usage:
        limiter = RateLimit(app)

        @limiter.limit("5/minute")
        @app.route("/api/resource")
        def resource():
            ...
    """

    def __init__(self, app=None):
        from .. import bustapi_core

        self._limiter = bustapi_core.PyRateLimiter()
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize with application instance."""
        app.extensions["rate_limit"] = self

    def limit(self, limit_string: str, key_func=None):
        """
        Decorator to limit access to a specific route.

        Args:
            limit_string: String in format "count/period" (e.g. "5/minute", "1/second")
            key_func: Optional function to generate a custom key. Defaults to remote IP.
        """
        count, period_seconds = self._parse_limit_string(limit_string)

        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Determine key
                # Default to IP from request context if available
                # We need to import request inside wrapper to avoid circular imports or context issues
                from ..http.request import request

                key = "global"
                if key_func:
                    key = key_func()
                elif request:
                    # Naive IP check, similar to Security class
                    # Ideally we trust X-Forwarded-For if behind proxy
                    key = request.headers.get(
                        "X-Forwarded-For", request.remote_addr or "unknown"
                    )

                # Combine with route endpoint or function name to make it per-route
                route_key = f"{key}:{f.__name__}"

                if not self._limiter.check_limit(route_key, count, period_seconds):
                    abort(429, f"Rate limit exceeded: {limit_string}")

                return f(*args, **kwargs)

            return wrapper

        return decorator

    def _parse_limit_string(self, limit_string: str) -> Tuple[int, int]:
        """
        Parse a limit string like "5/minute" into (count, period_seconds).
        """
        try:
            parts = limit_string.split("/")
            if len(parts) != 2:
                raise ValueError

            count = int(parts[0])
            period_str = parts[1].lower()

            if period_str.startswith("second") or period_str == "s":
                period = 1
            elif period_str.startswith("minute") or period_str == "m":
                period = 60
            elif period_str.startswith("hour") or period_str == "h":
                period = 3600
            elif period_str.startswith("day") or period_str == "d":
                period = 86400
            else:
                raise ValueError("Unknown period")

            return count, period
        except ValueError:
            raise ValueError(
                f"Invalid limit string: '{limit_string}'. Expected format: 'count/period' (e.g. '5/minute')"
            ) from None
