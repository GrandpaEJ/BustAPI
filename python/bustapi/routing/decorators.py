"""
Route decorators for BustAPI - Flask-compatible routing.
"""

import inspect
import re
from typing import Any, Callable, Optional


class RouteRegistration:
    """Mixin providing Flask-compatible route decorators."""

    def add_url_rule(
        self,
        rule: str,
        endpoint: Optional[str] = None,
        view_func: Optional[Callable] = None,
        provide_automatic_options: Optional[bool] = None,
        **options,
    ) -> None:
        """
        Connect a URL rule. Works exactly like the route decorator.

        Args:
            rule: The URL rule string
            endpoint: The endpoint for the registered URL rule
            view_func: The function to call when serving a request
            provide_automatic_options: Add OPTIONS handling automatically
            **options: Additional options (methods, etc.)
        """
        from ..dispatch import (
            create_async_raw_wrapper,
            create_async_wrapper,
            create_raw_wrapper,
            create_sync_wrapper,
        )

        if view_func is None:
            raise ValueError("view_func required")

        if endpoint is None:
            endpoint = view_func.__name__

        methods = options.get("methods", ["GET"])
        if isinstance(methods, str):
            methods = [methods]

        # Check for raw mode
        is_raw = options.pop("raw", False)

        self.view_functions[endpoint] = view_func
        self.url_map[rule] = {"endpoint": endpoint, "methods": methods}

        # Register parameter validators for this route (skip for raw?)
        # Raw mode users handle their own validation, but registering specs doesn't hurt.
        for method in methods:
            self._register_func_params(rule, method, view_func)

        # Register with Rust backend
        for method in methods:
            if inspect.iscoroutinefunction(view_func):
                if is_raw:
                    wrapper = create_async_raw_wrapper(view_func)
                else:
                    wrapper = create_async_wrapper(self, view_func, rule)

                self._rust_app.add_async_route(method, rule, wrapper)
            else:
                if is_raw:
                    wrapper = create_raw_wrapper(view_func)
                else:
                    wrapper = create_sync_wrapper(self, view_func, rule)

                self._rust_app.add_route(method, rule, wrapper)

    def route(self, rule: str, **options) -> Callable:
        """
        Flask-compatible route decorator.

        Args:
            rule: URL rule as string
            **options: Additional options including methods, defaults, etc.

        Returns:
            Decorator function

        Example:
            @app.route('/users/<int:id>', methods=['GET', 'POST'])
            def user(id):
                return f'User {id}'
        """

        def decorator(f: Callable) -> Callable:
            self.add_url_rule(rule, view_func=f, **options)
            return f

        return decorator

    def get(self, rule: str, **options) -> Callable:
        """Convenience decorator for GET routes."""
        return self.route(rule, methods=["GET"], **options)

    def post(self, rule: str, **options) -> Callable:
        """Convenience decorator for POST routes."""
        return self.route(rule, methods=["POST"], **options)

    def put(self, rule: str, **options) -> Callable:
        """Convenience decorator for PUT routes."""
        return self.route(rule, methods=["PUT"], **options)

    def delete(self, rule: str, **options) -> Callable:
        """Convenience decorator for DELETE routes."""
        return self.route(rule, methods=["DELETE"], **options)

    def patch(self, rule: str, **options) -> Callable:
        """Convenience decorator for PATCH routes."""
        return self.route(rule, methods=["PATCH"], **options)

    def head(self, rule: str, **options) -> Callable:
        """Convenience decorator for HEAD routes."""
        return self.route(rule, methods=["HEAD"], **options)

    def options(self, rule: str, **options) -> Callable:
        """Convenience decorator for OPTIONS routes."""
        return self.route(rule, methods=["OPTIONS"], **options)

    def turbo_route(
        self, rule: str, methods: list = None, cache_ttl: int = 0
    ) -> Callable:
        """
        Ultra-fast route decorator for maximum performance.

        Supports both static and dynamic routes:
        - Static: `/health`, `/api/version`
        - Dynamic: `/users/<int:id>`, `/posts/<int:id>/comments/<int:cid>`

        Path parameters are parsed in Rust for zero Python overhead.

        Args:
            rule: Route pattern (e.g., "/users/<int:id>")
            methods: List of HTTP methods (default: ["GET"])
            cache_ttl: Cache time-to-live in seconds (default: 0 = no cache)

        Limitations:
            - No `request` object access
            - No middleware, sessions, or auth support
            - Only supports dict/list/str returns

        Example:
            @app.turbo_route("/health")
            def health():
                return {"status": "ok"}

            @app.turbo_route("/users/<int:id>")
            def get_user(id: int):
                return {"id": id, "name": "Alice"}
        """
        if methods is None:
            methods = ["GET"]

        # Parse route pattern for typed params
        param_specs = self._parse_turbo_params(rule)

        def decorator(f: Callable) -> Callable:
            endpoint = f.__name__
            self.view_functions[endpoint] = f
            self.url_map[rule] = {"endpoint": endpoint, "methods": methods}

            if param_specs:
                # Dynamic turbo route with typed params
                from ..dispatch import create_typed_turbo_wrapper

                param_names = [name for name, _ in param_specs]
                turbo_wrapped = create_typed_turbo_wrapper(f, param_names)
                param_types = dict(param_specs)

                for method in methods:
                    self._rust_app.add_typed_turbo_route(
                        method, rule, turbo_wrapped, param_types, cache_ttl
                    )
            else:
                # Static turbo route (no params)
                from ..dispatch import create_turbo_wrapper

                turbo_wrapped = create_turbo_wrapper(f)

                for method in methods:
                    self._rust_app.add_typed_turbo_route(
                        method, rule, turbo_wrapped, {}, cache_ttl
                    )

            return f

        return decorator

    def static_route(
        self, rule: str, methods: list = None, content_type: str = "application/json"
    ) -> Callable:
        """
        Register a purely static route served directly from Rust memory.

        The decorated function is executed ONCE at startup. Its return value
        is serialized and stored in the Rust backend.

        Runtime cost: 0 Python ops.

        Args:
            rule: URL rule
            methods: HTTP methods (default: ["GET"])
            content_type: Content-Type header (default: "application/json")

        Example:
            @app.static_route("/api/version")
            def version():
                return {"version": "1.0.0"}
        """
        if methods is None:
            methods = ["GET"]

        def decorator(f: Callable) -> Callable:
            # Execute function immediately to get static content
            result = f()

            # Serialize content
            if isinstance(result, (dict, list)):
                import json

                body = json.dumps(result)
            elif isinstance(result, str):
                body = result
            else:
                body = str(result)

            # Register with Rust backend
            if hasattr(self, "_rust_app"):
                for method in methods:
                    self._rust_app.add_fast_route(method, rule, body, content_type)

            return f

        return decorator

        return decorator

    def compiled_route(self, rule: str, methods: list = None) -> Callable:
        """
        Register a compiled dynamic route (Rust-only execution).

        The decorated function is executed ONCE at startup with "TraceValue" objects.
        The result is compiled into a pure Rust template.

        Runtime cost: 0 Python ops.

        Args:
            rule: Route pattern
            methods: HTTP methods (default: ["GET"])

        Example:
            @app.compiled_route("/user/<int:id>")
            def get_user(id):
                return {"id": id, "status": "active"}
        """
        if methods is None:
            methods = ["GET"]

        # Parse params
        param_specs = self._parse_turbo_params(rule)

        def decorator(f: Callable) -> Callable:
            # Import TraceValue and TraceExpr
            try:
                from ..bustapi_core import TraceExpr, TraceValue
            except ImportError:
                # Fallback for dev/mocking
                class TraceValue:
                    def __init__(self, n, t):
                        pass

                    def __add__(self, o):
                        return TraceExpr()

                    def __sub__(self, o):
                        return TraceExpr()

                    def __mul__(self, o):
                        return TraceExpr()

                    def __truediv__(self, o):
                        return TraceExpr()

                class TraceExpr:
                    def __add__(self, o):
                        return TraceExpr()

                    def __sub__(self, o):
                        return TraceExpr()

                    def __mul__(self, o):
                        return TraceExpr()

                    def __truediv__(self, o):
                        return TraceExpr()

            # Create trace objects
            traces = {}
            for name, type_str in param_specs:
                traces[name] = TraceValue(name, type_str)

            # Execute function to get template structure
            try:
                # We assume the function uses matching argument names
                result = f(**traces)
            except Exception as e:
                raise RuntimeError(  # noqa: B904
                    f"Failed to compile route '{rule}'. Ensure handler accepts arguments matching route parameters. Error: {e}"
                )

            # Register with Rust backend
            param_types = dict(param_specs)
            if hasattr(self, "_rust_app"):
                for method in methods:
                    self._rust_app.add_compiled_route(method, rule, result, param_types)

            return f

        return decorator

    def _parse_turbo_params(self, rule: str) -> list:
        """
        Parse route pattern and extract typed parameters.

        Args:
            rule: Route pattern like "/users/<int:id>" or "/posts/<id>"

        Returns:
            List of (name, type_str) tuples, e.g., [("id", "int"), ("name", "str")]
        """
        params = []
        # Match <type:name> or <name> patterns
        pattern = r"<(int|float|str|path)?:?(\w+)>"

        for match in re.finditer(pattern, rule):
            type_str = match.group(1) or "str"  # Default to str
            name = match.group(2)
            params.append((name, type_str))

        return params

    def websocket(self, rule: str, config: Optional[Any] = None) -> Callable:
        """
        WebSocket route decorator for real-time bidirectional communication.

        Args:
            rule: URL path for the WebSocket endpoint
            config: Optional WebSocketConfig instance
        """
        from ..websocket import WebSocketHandler

        def decorator(f: Callable) -> Callable:
            endpoint = f.__name__
            handler = WebSocketHandler(f)
            f._websocket_handler = handler
            f._websocket_path = rule

            # Store for later registration during server startup
            if not hasattr(self, "_websocket_routes"):
                self._websocket_routes = {}
            self._websocket_routes[rule] = handler

            self.view_functions[endpoint] = f
            self.url_map[rule] = {
                "endpoint": endpoint,
                "methods": ["GET"],
                "websocket": True,
            }

            # Register WebSocket handler with Rust backend
            if hasattr(self, "_rust_app"):
                self._rust_app.add_websocket_route(rule, handler, config)

            return f

        return decorator

    def turbo_websocket(
        self, rule: str, response_prefix: str = "Echo: ", config: Optional[Any] = None
    ) -> Callable:
        """
        Turbo WebSocket route - pure Rust, maximum performance.

        Unlike regular @app.websocket(), this handler runs entirely in Rust.
        The response_prefix is prepended to every received message.

        Args:
            rule: URL path for the WebSocket endpoint
            response_prefix: String to prepend to each echoed message
            config: Optional WebSocketConfig instance
        """

        def decorator(f: Callable) -> Callable:
            endpoint = f.__name__
            f._turbo_websocket_path = rule
            f._turbo_websocket_prefix = response_prefix

            self.view_functions[endpoint] = f
            self.url_map[rule] = {
                "endpoint": endpoint,
                "methods": ["GET"],
                "turbo_websocket": True,
            }

            # Register Turbo WebSocket handler with Rust backend
            if hasattr(self, "_rust_app"):
                self._rust_app.add_turbo_websocket_route(rule, response_prefix, config)

            return f

        return decorator
