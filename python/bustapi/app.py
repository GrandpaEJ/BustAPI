"""
BustAPI Application class - Flask-compatible web framework

This is the main application class that coordinates all components.
Mixins are used to keep the codebase modular and maintainable.
"""

import inspect
import os
from typing import Any, Callable, Dict, List, Optional, Type, Union

from .context import ContextMixin, _AppContext, _RequestContext
from .core.helpers import get_root_path
from .core.logging import get_logger
from .dispatch import create_async_wrapper, create_sync_wrapper
from .extraction import ExtractionMixin
from .hooks import HooksMixin
from .http.request import Request, _request_ctx
from .http.response import Response, make_response
from .middleware import MiddlewareManager
from .responses import HTMLResponse
from .routing.blueprints import Blueprint
from .routing.decorators import RoutingMixin
from .server.wsgi import WSGIAdapter
from .serving import run_server
from .sessions import SecureCookieSessionInterface


class BustAPI(RoutingMixin, ExtractionMixin, HooksMixin, ContextMixin, WSGIAdapter):
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
        redirect_slashes: bool = True,
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
        if import_name is None:
            import inspect

            # Auto-detect the caller's module name
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            import_name = module.__name__ if module else self.__class__.__module__

        self.import_name = import_name

        if root_path is None:
            root_path = get_root_path(self.import_name)
        self.root_path = root_path

        self.static_url_path = static_url_path

        if static_folder is None:
            static_folder = "static"
        if not os.path.isabs(static_folder):
            static_folder = os.path.join(root_path, static_folder)
        self.static_folder = static_folder

        if template_folder is None:
            template_folder = "templates"
        if not os.path.isabs(template_folder):
            template_folder = os.path.join(root_path, template_folder)
        self.template_folder = template_folder

        self.instance_relative_config = instance_relative_config
        self.redirect_slashes = redirect_slashes

        # Configuration dictionary
        self.config: Dict[str, Any] = {}

        # Extension registry
        self.extensions: Dict[str, Any] = {}

        # View functions registry
        self.view_functions: Dict[str, Callable] = {}
        self.error_handler_spec: Dict[Union[int, Type[Exception]], Callable] = {}
        self.before_request_funcs: List[Callable] = []
        self.after_request_funcs: List[Callable] = []
        self.teardown_request_funcs: List[Callable] = []
        self.teardown_appcontext_funcs: List[Callable] = []
        self.blueprints: Dict[str, Blueprint] = {}

        # URL map and rules
        self.url_map: Dict[str, Dict] = {}

        # Parameter validation metadata
        self.path_validators: Dict[tuple, Dict[str, Any]] = {}
        self.query_validators: Dict[tuple, Dict[str, tuple]] = {}
        self.body_validators: Dict[tuple, Dict[str, tuple]] = {}
        self.dependencies: Dict[tuple, Dict[str, Any]] = {}

        # Templating
        self.jinja_env = None

        # Initialize logger
        try:
            self.logger = get_logger("bustapi.app")
        except Exception:
            self.logger = None

        # Flask compatibility attributes
        self.debug = False
        self.testing = False
        self.secret_key = None
        self.permanent_session_lifetime = None
        self.use_x_sendfile = False
        self.json_encoder = None
        self.json_decoder = None
        self.jinja_options = {}
        self.got_first_request = False
        self.shell_context_processors = []
        self.cli = None
        self.instance_path = None
        self.open_session = None
        self.save_session = None
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

        # Middleware and Sessions
        self.middleware_manager = MiddlewareManager()
        self.session_interface = SecureCookieSessionInterface()

        # Initialize Rust backend
        self._rust_app = None
        self._init_rust_backend()

    def _init_rust_backend(self):
        """Initialize the Rust backend application."""
        try:
            from . import bustapi_core

            self._rust_app = bustapi_core.create_app()

            # Register static file handler
            # print(f"DEBUG: static_folder={self.static_folder}, isdir={os.path.isdir(self.static_folder) if self.static_folder else 'None'}")
            if self.static_folder and os.path.isdir(self.static_folder):
                # self._rust_app.set_static_folder(self.static_folder)  # Not implemented in Rust
                static_url = self.static_url_path or "/static"
                # print(f"DEBUG: Adding static route {static_url} -> {self.static_folder}")
                self._rust_app.add_static_route(static_url, self.static_folder)

            # Register template folder
            if self.template_folder and os.path.isdir(self.template_folder):
                self._rust_app.set_template_folder(self.template_folder)

        except ImportError as e:
            raise RuntimeError(
                f"BustAPI requires the Rust backend. Build with: maturin develop\n{e}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Rust backend: {e}") from e

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

            full_endpoint = f"{blueprint.name}.{endpoint}"
            self.view_functions[full_endpoint] = view_func

            # Register with Rust backend
            for method in methods:
                if inspect.iscoroutinefunction(view_func):
                    self._rust_app.add_async_route(
                        method, rule, create_async_wrapper(self, view_func, rule)
                    )
                else:
                    self._rust_app.add_route(
                        method, rule, create_sync_wrapper(self, view_func, rule)
                    )

    def _make_response(self, *args) -> Response:
        """Convert various return types to Response objects."""
        return make_response(*args)

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

    def create_jinja_env(self):
        """Create and cache a Jinja2 environment."""
        if self.jinja_env is None:
            try:
                from .templating import create_jinja_env as _create_env

                self.jinja_env = _create_env(self.template_folder)
            except Exception as e:
                raise RuntimeError(f"Failed to create Jinja environment: {e}") from e
        return self.jinja_env

    def render_template(self, template_name: str, **context) -> Response:
        """Render a template using the native Rust engine."""
        import json

        html_content = self._rust_app.render_template(
            template_name, json.dumps(context)
        )
        return HTMLResponse(html_content)

    def _handle_exception(self, exception: Exception) -> Response:
        """Handle exceptions and return appropriate error responses."""
        for exc_class_or_code, handler in self.error_handler_spec.items():
            if isinstance(exc_class_or_code, type) and isinstance(
                exception, exc_class_or_code
            ):
                return self._make_response(handler(exception))
            elif isinstance(exc_class_or_code, int):
                if hasattr(exception, "code") and exception.code == exc_class_or_code:
                    return self._make_response(handler(exception))

        status = getattr(exception, "code", 500) if hasattr(exception, "code") else 500
        return Response(f"Internal Server Error: {str(exception)}", status=status)

    def _response_to_rust_format(self, response: Response) -> Union[tuple, Response]:
        """Convert Python Response object to format expected by Rust."""
        # Check for FileResponse (has path attribute)
        if hasattr(response, "path"):
            return response

        # Check for StreamingResponse (has content attribute)
        if hasattr(response, "content"):
            return response

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
        workers: Optional[int] = None,
        reload: bool = False,
        server: str = "rust",
        **options,
    ) -> None:
        """
        Run the application server (Flask-compatible).

        Args:
            host: Hostname to bind to (default: 127.0.0.1)
            port: Port to bind to (default: 5000)
            debug: Enable debug mode
            load_dotenv: Load environment variables from .env file
            workers: Number of worker threads
            reload: Enable auto-reload on code changes
            server: Server backend ('rust', 'uvicorn', 'gunicorn', 'hypercorn')
            **options: Additional server options
        """
        if debug:
            self.config["DEBUG"] = True
            # self._setup_debug_logging()  # Handled by Rust backend now for better coverage

        # Handle hot reload
        if reload or debug:
            self._enable_hot_reload()

        if workers is None:
            import multiprocessing

            workers = 1 if debug else multiprocessing.cpu_count()

        # Dispatch to appropriate server
        if server == "rust":
            self._run_rust_server(host, port, workers, debug)
        elif server == "uvicorn":
            self._run_uvicorn(host, port, workers, debug, **options)
        elif server == "gunicorn":
            self._run_gunicorn(host, port, workers, debug, **options)
        elif server == "hypercorn":
            self._run_hypercorn(host, port, workers, debug, **options)

    def _setup_debug_logging(self):
        """Setup request logging for debug mode."""

        def _debug_start_timer():
            try:
                import time

                from bustapi import request

                request.start_time = time.time()
            except ImportError:
                pass

        def _debug_log_request(response):
            try:
                import time

                from bustapi import logging, request

                start_time = getattr(request, "start_time", time.time())
                duration = time.time() - start_time
                logging.log_request(
                    request.method, request.path, response.status_code, duration
                )
            except ImportError:
                pass
            return response

        self.before_request(_debug_start_timer)
        self.after_request(_debug_log_request)

    def _enable_hot_reload(self):
        """Enable Rust-native hot reload."""
        if os.environ.get("BUSTAPI_RELOADER_RUN") != "true":
            try:
                from . import bustapi_core

                bustapi_core.enable_hot_reload(".")
            except ImportError:
                print("⚠️ Native hot reload not available in this build.")
            except Exception as e:
                print(f"⚠️ Failed to enable hot reload: {e}")

    def _run_rust_server(self, host, port, workers, debug):
        """Run the native Rust HTTP server."""
        if workers > 1 and not debug:
            from .multiprocess import spawn_workers

            spawn_workers(self._rust_app, host, port, workers, debug)
            return

        try:
            self._rust_app.run(host, port, workers, debug)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"❌ Server error: {e}")

    def _run_uvicorn(self, host, port, workers, debug, **options):
        """Run with Uvicorn ASGI server."""
        try:
            import uvicorn

            config = uvicorn.Config(
                app=self.asgi_app,
                host=host,
                port=port,
                workers=workers,
                log_level="debug" if debug else "info",
                interface="asgi3",
                **options,
            )
            server = uvicorn.Server(config)
            server.run()
        except ImportError:
            print("❌ 'uvicorn' not installed. Install via `pip install uvicorn`.")
        except Exception as e:
            print(f"❌ Uvicorn error: {e}")

    def _run_gunicorn(self, host, port, workers, debug, **options):
        """Run with Gunicorn WSGI server."""
        try:
            from gunicorn.app.base import BaseApplication

            class StandaloneApplication(BaseApplication):
                def __init__(self, app, opts=None):
                    self.application = app
                    self.options = opts or {}
                    super().__init__()

                def load_config(self):
                    config = {
                        key: value
                        for key, value in self.options.items()
                        if key in self.cfg.settings and value is not None
                    }
                    for key, value in config.items():
                        self.cfg.set(key.lower(), value)

                def load(self):
                    return self.application

            gunicorn_options = {
                "bind": f"{host}:{port}",
                "workers": workers,
                "loglevel": "debug" if debug else "info",
                **options,
            }

            StandaloneApplication(self, gunicorn_options).run()
        except ImportError:
            print("❌ 'gunicorn' not installed. Install via `pip install gunicorn`.")
        except Exception as e:
            print(f"❌ Gunicorn error: {e}")

    def _run_hypercorn(self, host, port, workers, debug, **options):
        """Run with Hypercorn ASGI server."""
        try:
            import asyncio

            from hypercorn.asyncio import serve
            from hypercorn.config import Config

            config = Config()
            config.bind = [f"{host}:{port}"]
            config.workers = workers
            config.loglevel = "debug" if debug else "info"

            asyncio.run(serve(self.asgi_app, config))
        except ImportError:
            print("❌ 'hypercorn' not installed. Install via `pip install hypercorn`.")
        except Exception as e:
            print(f"❌ Hypercorn error: {e}")

    async def run_async(
        self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False, **options
    ) -> None:
        """Run the application server asynchronously."""
        if debug:
            self.config["DEBUG"] = True
            self._setup_debug_logging()

        try:
            await self._rust_app.run_async(host, port, debug)
        except Exception as e:
            print(f"❌ Async server error: {e}")

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
