"""
BustAPI Application class - Flask-compatible web framework
"""

import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union

from .blueprints import Blueprint
from .logging import get_logger
from .request import Request, _request_ctx
from .response import Response, make_response


class BustAPI:
    """
    Flask-compatible application class built on Rust backend.

    Example:
        app = BustAPI()

        @app.route('/')
        def hello():
            return 'Hello, World!'

        app.run()
    """

    def __init__(
        self,
        import_name: str = None,
        static_url_path: Optional[str] = None,
        static_folder: Optional[str] = None,
        template_folder: Optional[str] = None,
        instance_relative_config: bool = False,
        root_path: Optional[str] = None,
        # FastAPI-style parameters
        title: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        docs_url: Optional[str] = None,
        redoc_url: Optional[str] = None,
        openapi_url: Optional[str] = None,
    ):
        """
        Initialize BustAPI application.

        Args:
            import_name: Name of the application package
            static_url_path: URL path for static files
            static_folder: Filesystem path to static files
            template_folder: Filesystem path to templates
            instance_relative_config: Enable instance relative config
            root_path: Root path for the application
        """
        self.import_name = import_name or self.__class__.__module__
        self.static_url_path = static_url_path
        self.static_folder = static_folder
        self.template_folder = template_folder
        self.instance_relative_config = instance_relative_config
        self.root_path = root_path

        # Configuration dictionary
        self.config: Dict[str, Any] = {}

        # Extension registry
        self.extensions: Dict[str, Any] = {}

        # Route handlers
        self._view_functions: Dict[str, Callable] = {}

        # Error handlers
        self.error_handler_spec: Dict[Union[int, Type[Exception]], Callable] = {}

        # Before/after request handlers
        self.before_request_funcs: List[Callable] = []
        self.after_request_funcs: List[Callable] = []
        self.teardown_request_funcs: List[Callable] = []
        self.teardown_appcontext_funcs: List[Callable] = []

        # Blueprint registry
        self.blueprints: Dict[str, Blueprint] = {}

        # URL map and rules
        # url_map maps rule -> {endpoint, methods}
        self.url_map: Dict[str, Dict] = {}

        # Jinja environment (placeholder for template support)
        self.jinja_env = None

        # FastAPI-style configuration
        self.title = title or "BustAPI"
        self.description = description or "A high-performance Python web framework"
        self.version = version or "1.0.0"
        self.docs_url = docs_url
        self.redoc_url = redoc_url
        self.openapi_url = openapi_url

        # Initialize colorful logger
        try:
            self.logger = get_logger("bustapi.app")
        except Exception:
            # Fallback if logging module has issues
            self.logger = None

        # Flask compatibility attributes
        self.debug = False
        self.testing = False
        self.secret_key = None
        self.permanent_session_lifetime = None
        self.use_x_sendfile = False
        self.logger = None
        self.json_encoder = None
        self.json_decoder = None
        self.jinja_options = {}
        self.got_first_request = False
        self.shell_context_processors = []
        self.cli = None
        self.instance_path = None
        self.open_session = None
        self.save_session = None
        self.session_interface = None
        self.wsgi_app = None
        self.response_class = None
        self.request_class = None
        self.test_client_class = None
        self.test_cli_runner_class = None
        self.url_rule_class = None
        self.url_map_class = None
        self.subdomain_matching = False
        self.url_defaults = None
        self.template_context_processors = {}
        self._template_fragment_cache = None

        # Initialize Rust backend
        self._rust_app = None
        self._init_rust_backend()
        # Register auto documentation endpoints
        try:
            if self.openapi_url:
                self.get(self.openapi_url)(self._openapi_route)
            if self.docs_url:
                self.get(self.docs_url)(self._swagger_ui)
            if self.redoc_url:
                self.get(self.redoc_url)(self._redoc_ui)
        except Exception:
            # ignore registration errors in environments where Rust backend
            # isn't available
            pass

    def _init_rust_backend(self):
        """Initialize the Rust backend application."""
        try:
            from . import bustapi_core

            self._rust_app = bustapi_core.PyBustApp()
        except ImportError as e:
            raise RuntimeError(f"Failed to import Rust backend: {e}")

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
            endpoint = options.pop("endpoint", f.__name__)
            methods = options.pop("methods", ["GET"])

            # Store view function
            self._view_functions[endpoint] = f

            # Store the rule and methods for OpenAPI generation and debugging
            self.url_map[rule] = {"endpoint": endpoint, "methods": methods}

            # Register with Rust backend
            for method in methods:
                if inspect.iscoroutinefunction(f):
                    # Async handler executed synchronously via asyncio.run
                    # inside wrapper
                    self._rust_app.add_route(
                        method, rule, self._wrap_async_handler(f, rule)
                    )
                else:
                    # Sync handler
                    self._rust_app.add_route(
                        method, rule, self._wrap_sync_handler(f, rule)
                    )

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

    # Flask compatibility methods
    def shell_context_processor(self, f):
        """Register a shell context processor function."""
        self.shell_context_processors.append(f)
        return f

    def make_shell_context(self):
        """Create shell context."""
        context = {"app": self}
        for processor in self.shell_context_processors:
            context.update(processor())
        return context

    def app_context(self):
        """Create application context."""
        return _AppContext(self)

    def request_context(self, environ_or_request):
        """Create request context."""
        return _RequestContext(self, environ_or_request)

    def test_request_context(self, *args, **kwargs):
        """Create test request context."""
        return _RequestContext(self, None)

    def preprocess_request(self):
        """Preprocess request."""
        for func in self.before_request_funcs:
            result = func()
            if result is not None:
                return result

    def process_response(self, response):
        """Process response."""
        for func in self.after_request_funcs:
            response = func(response)
        return response

    def do_teardown_request(self, exc=None):
        """Teardown request."""
        for func in self.teardown_request_funcs:
            func(exc)

    def do_teardown_appcontext(self, exc=None):
        """Teardown app context."""
        for func in self.teardown_appcontext_funcs:
            func(exc)

    def make_default_options_response(self):
        """Make default OPTIONS response."""
        from .response import Response

        return Response("", 200, {"Allow": "GET,HEAD,POST,OPTIONS"})

    def create_jinja_environment(self):
        """Create Jinja2 environment."""
        if self.jinja_env is None:
            try:
                from jinja2 import Environment, FileSystemLoader

                template_folder = self.template_folder or "templates"
                self.jinja_env = Environment(
                    loader=FileSystemLoader(template_folder), **self.jinja_options
                )
            except ImportError:
                pass
        return self.jinja_env

    def _extract_path_params(self, rule: str, path: str):
        """Extract path params from a Flask-style rule like '/greet/<name>' or '/users/<int:id>'."""
        rule_parts = rule.strip("/").split("/")
        path_parts = path.strip("/").split("/")
        args = []
        kwargs = {}
        if len(rule_parts) != len(path_parts):
            return args, kwargs
        for rp, pp in zip(rule_parts, path_parts):
            if rp.startswith("<") and rp.endswith(">"):
                inner = rp[1:-1]  # strip < >
                if ":" in inner:
                    typ, name = inner.split(":", 1)
                    typ = typ.strip()
                    name = name.strip()
                else:
                    typ = "str"
                    name = inner.strip()
                val = pp
                if typ == "int":
                    try:
                        val = int(pp)
                    except ValueError:
                        val = pp
                # Only populate kwargs to avoid duplicate positional+keyword arguments
                kwargs[name] = val
        return args, kwargs

    def before_request(self, f: Callable) -> Callable:
        """
        Register function to run before each request.

        Args:
            f: Function to run before request

        Returns:
            The original function
        """
        self.before_request_funcs.append(f)
        return f

    def after_request(self, f: Callable) -> Callable:
        """
        Register function to run after each request.

        Args:
            f: Function to run after request

        Returns:
            The original function
        """
        self.after_request_funcs.append(f)
        return f

    def teardown_request(self, f: Callable) -> Callable:
        """
        Register function to run after each request, even if an exception occurred.

        Args:
            f: Function to run on teardown

        Returns:
            The original function
        """
        self.teardown_request_funcs.append(f)
        return f

    def teardown_appcontext(self, f: Callable) -> Callable:
        """
        Register function to run when application context is torn down.

        Args:
            f: Function to run on app context teardown

        Returns:
            The original function
        """
        self.teardown_appcontext_funcs.append(f)
        return f

    def errorhandler(self, code_or_exception: Union[int, Type[Exception]]) -> Callable:
        """
        Register error handler for HTTP status codes or exceptions.

        Args:
            code_or_exception: HTTP status code or exception class

        Returns:
            Decorator function
        """

        def decorator(f: Callable) -> Callable:
            self.error_handler_spec[code_or_exception] = f
            return f

        return decorator

    def register_blueprint(self, blueprint: Blueprint, **options) -> None:
        """
        Register a blueprint with the application.

        Args:
            blueprint: Blueprint instance to register
            **options: Additional options for blueprint registration
        """
        url_prefix = options.get("url_prefix", blueprint.url_prefix)

        # Store blueprint
        self.blueprints[blueprint.name] = blueprint

        # Register blueprint routes with the application
        for rule, endpoint, view_func, methods in blueprint.deferred_functions:
            if url_prefix:
                rule = url_prefix.rstrip("/") + "/" + rule.lstrip("/")

            # Create route with blueprint endpoint
            full_endpoint = f"{blueprint.name}.{endpoint}"
            self._view_functions[full_endpoint] = view_func

            # Register with Rust backend
            for method in methods:
                if inspect.iscoroutinefunction(view_func):
                    # Async handler executed synchronously via asyncio.run inside wrapper
                    self._rust_app.add_route(
                        method, rule, self._wrap_async_handler(view_func, rule)
                    )
                else:
                    self._rust_app.add_route(
                        method, rule, self._wrap_sync_handler(view_func, rule)
                    )

    def _wrap_sync_handler(self, handler: Callable, rule: str) -> Callable:
        """Wrap handler with request context, middleware, and path param support."""

        @wraps(handler)
        def wrapper(rust_request):
            try:
                # Convert Rust request to Python Request object
                request = Request._from_rust_request(rust_request)

                # Set request context
                _request_ctx.set(request)

                # Run before request handlers
                for before_func in self.before_request_funcs:
                    result = before_func()
                    if result is not None:
                        return self._make_response(result)

                # Extract path params from rule and path
                args, kwargs = self._extract_path_params(rule, request.path)

                # Call the actual handler (Flask-style handlers take path params)
                # Note: Async handlers are now handled directly by Rust PyAsyncRouteHandler
                # This wrapper should only handle sync functions for better performance
                result = handler(**kwargs)

                # Handle tuple responses properly
                if isinstance(result, tuple):
                    response = self._make_response(*result)
                else:
                    response = self._make_response(result)

                # Run after request handlers
                for after_func in self.after_request_funcs:
                    response = after_func(response) or response

                # Convert Python Response to dict/tuple for Rust
                return self._response_to_rust_format(response)

            except Exception as e:
                # Handle errors
                error_response = self._handle_exception(e)
                return self._response_to_rust_format(error_response)
            finally:
                # Teardown handlers
                for teardown_func in self.teardown_request_funcs:
                    try:
                        teardown_func(None)
                    except Exception:
                        pass

                # Clear request context
                _request_ctx.set(None)

        return wrapper

    def _wrap_async_handler(self, handler: Callable, rule: str) -> Callable:
        """Wrap asynchronous handler; executed synchronously via asyncio.run for now."""

        @wraps(handler)
        def wrapper(rust_request):
            try:
                # Convert Rust request to Python Request object
                request = Request._from_rust_request(rust_request)

                # Set request context
                _request_ctx.set(request)

                # Run before request handlers
                for before_func in self.before_request_funcs:
                    result = before_func()
                    if result is not None:
                        return self._make_response(result)

                # Extract path params
                args, kwargs = self._extract_path_params(rule, request.path)

                # Call the handler (sync only - async handled by Rust)
                # Note: Async handlers are now handled directly by Rust PyAsyncRouteHandler
                result = handler(**kwargs)

                # Handle tuple responses properly
                if isinstance(result, tuple):
                    response = self._make_response(*result)
                else:
                    response = self._make_response(result)

                # Run after request handlers
                for after_func in self.after_request_funcs:
                    response = after_func(response) or response

                # Convert Python Response to dict/tuple for Rust
                return self._response_to_rust_format(response)

            except Exception as e:
                # Handle errors
                error_response = self._handle_exception(e)
                return self._response_to_rust_format(error_response)
            finally:
                # Teardown handlers
                for teardown_func in self.teardown_request_funcs:
                    try:
                        teardown_func(None)
                    except Exception:
                        pass

                # Clear request context
                _request_ctx.set(None)

        return wrapper

    def _make_response(self, *args) -> Response:
        """Convert various return types to Response objects."""
        return make_response(*args)

    # --- Templating helpers ---
    def create_jinja_env(self):
        """Create and cache a Jinja2 environment using the application's template_folder."""
        if self.jinja_env is None:
            try:
                from .templating import create_jinja_env as _create_env

                self.jinja_env = _create_env(self.template_folder)
            except Exception as e:
                raise RuntimeError(f"Failed to create Jinja environment: {e}")
        return self.jinja_env

    def render_template(self, template_name: str, **context) -> str:
        """Render a template using the app's Jinja environment."""
        env = self.create_jinja_env()
        from .templating import render_template as _render

        return _render(env, template_name, context)

    # --- OpenAPI generation ---
    def _generate_openapi(self) -> Dict:
        """Generate OpenAPI 3.1.0 specification for the application."""
        try:
            from .openapi.utils import get_openapi_spec

            # Extract route information from url_map
            routes = []
            for rule, meta in self.url_map.items():
                methods = meta.get("methods", ["GET"])
                endpoint = meta.get("endpoint")
                handler = self._view_functions.get(endpoint)

                routes.append(
                    {
                        "path": rule,
                        "methods": methods,
                        "handler": handler,
                        "endpoint": endpoint,
                    }
                )

            # Generate OpenAPI spec using our custom implementation
            return get_openapi_spec(
                title=self.title,
                version=self.version,
                description=self.description,
                routes=routes,
                servers=[{"url": "/", "description": "Development server"}],
            )

        except Exception:
            # Fallback to simple implementation if there are issues
            info = {"title": self.title, "version": self.version}
            if self.description:
                info["description"] = self.description

            paths: Dict[str, Dict] = {}
            for rule, meta in self.url_map.items():
                methods = meta.get("methods", ["GET"])
                paths.setdefault(rule, {})
                for m in methods:
                    endpoint = meta.get("endpoint")
                    view = self._view_functions.get(endpoint)
                    summary = None
                    if view is not None:
                        summary = (
                            (view.__doc__ or "").strip().splitlines()[0]
                            if view.__doc__
                            else view.__name__
                        )
                    paths[rule][m.lower()] = {
                        "summary": summary or endpoint,
                        "operationId": endpoint,
                        "responses": {"200": {"description": "Successful response"}},
                    }

            return {"openapi": "3.1.0", "info": info, "paths": paths}

    def _openapi_route(self):
        """Simple route handler that returns the generated OpenAPI JSON."""
        return self._generate_openapi()

    def _swagger_ui(self):
        """Swagger UI documentation page."""
        openapi_url = self.openapi_url or "/openapi.json"
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.title} - Swagger UI</title>
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
            <style>
                html {{ box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }}
                *, *:before, *:after {{ box-sizing: inherit; }}
                body {{ margin:0; background: #fafafa; }}
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
            <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
            <script>
                window.onload = function() {{
                    const ui = SwaggerUIBundle({{
                        url: '{openapi_url}',
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIStandalonePreset
                        ],
                        plugins: [
                            SwaggerUIBundle.plugins.DownloadUrl
                        ],
                        layout: "StandaloneLayout"
                    }});
                }};
            </script>
        </body>
        </html>
        """
        from .response import make_response

        response = make_response(html)
        response.headers["Content-Type"] = "text/html"
        return response

    def _redoc_ui(self):
        """ReDoc documentation page."""
        openapi_url = self.openapi_url or "/openapi.json"
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.title} - ReDoc</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
            <style>
                body {{ margin: 0; padding: 0; }}
            </style>
        </head>
        <body>
            <redoc spec-url='{openapi_url}'></redoc>
            <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"></script>
        </body>
        </html>
        """
        from .response import make_response

        response = make_response(html)
        response.headers["Content-Type"] = "text/html"
        return response

    def _handle_exception(self, exception: Exception) -> Response:
        """Handle exceptions and return appropriate error responses."""
        # Check for registered error handlers
        for exc_class_or_code, handler in self.error_handler_spec.items():
            if isinstance(exc_class_or_code, type) and isinstance(
                exception, exc_class_or_code
            ):
                return self._make_response(handler(exception))
            elif isinstance(exc_class_or_code, int):
                # For HTTP status code handlers, need to check if it matches
                # This is a simplified implementation
                pass

        # Default error response
        if hasattr(exception, "code"):
            status = getattr(exception, "code", 500)
        else:
            status = 500

        return Response(f"Internal Server Error: {str(exception)}", status=status)

    def _response_to_rust_format(self, response: Response) -> tuple:
        """Convert Python Response object to format expected by Rust."""
        # Return (body, status_code, headers) tuple
        headers_dict = {}
        if hasattr(response, "headers") and response.headers:
            headers_dict = dict(response.headers)

        body = (
            response.get_data(as_text=False)
            if hasattr(response, "get_data")
            else str(response).encode("utf-8")
        )
        status_code = response.status_code if hasattr(response, "status_code") else 200

        return (body.decode("utf-8", errors="replace"), status_code, headers_dict)

    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 5000,
        debug: bool = False,
        load_dotenv: bool = True,
        **options,
    ) -> None:
        """
        Run the application server (Flask-compatible).

        Args:
            host: Hostname to bind to
            port: Port to bind to
            debug: Enable debug mode
            load_dotenv: Load environment variables from .env file
            **options: Additional server options
        """
        if debug:
            self.config["DEBUG"] = True

        # Log startup with colorful output
        if self.logger:
            self.logger.log_startup(f"Starting {self.title} v{self.version}")
            self.logger.info(f"Listening on http://{host}:{port}")
            self.logger.info(f"Debug mode: {'ON' if debug else 'OFF'}")

            if self.docs_url:
                self.logger.info(f"📚 API docs: http://{host}:{port}{self.docs_url}")
            if self.redoc_url:
                self.logger.info(f"📖 ReDoc: http://{host}:{port}{self.redoc_url}")
        else:
            print(f"🚀 Starting {self.title} v{self.version}")
            print(f"📍 Listening on http://{host}:{port}")
            print(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")

            if self.docs_url:
                print(f"📚 API docs: http://{host}:{port}{self.docs_url}")
            if self.redoc_url:
                print(f"📖 ReDoc: http://{host}:{port}{self.redoc_url}")

        try:
            self._rust_app.run(host, port)
        except KeyboardInterrupt:
            if self.logger:
                self.logger.log_shutdown("Server stopped by user")
            else:
                print("\n🛑 Server stopped by user")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Server error: {e}")
            else:
                print(f"❌ Server error: {e}")

    async def run_async(
        self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False, **options
    ) -> None:
        """
        Run the application server asynchronously.

        Args:
            host: Hostname to bind to
            port: Port to bind to
            debug: Enable debug mode
            **options: Additional server options
        """
        if debug:
            self.config["DEBUG"] = True

        await self._rust_app.run_async(host, port)

    def test_client(self, use_cookies: bool = True, **kwargs):
        """
        Create a test client for the application.

        Args:
            use_cookies: Enable cookie support in test client
            **kwargs: Additional test client options

        Returns:
            TestClient instance
        """
        from .testing import TestClient

        return TestClient(self, use_cookies=use_cookies, **kwargs)




class _AppContext:
    """Application context manager."""

    def __init__(self, app: BustAPI):
        self.app = app

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class _RequestContext:
    """Request context manager."""

    def __init__(self, app: BustAPI, environ_or_request):
        self.app = app
        self.request = environ_or_request

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
