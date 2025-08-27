"""
BustAPI Application class - Flask-compatible web framework
"""

import inspect
import sys
from typing import Any, Callable, Dict, List, Optional, Union, Type
from functools import wraps
import asyncio
from contextvars import copy_context

from .request import Request, _request_ctx
from .response import Response, make_response
from .helpers import _get_current_object
from .blueprints import Blueprint


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

    def __init__(self, import_name: str = None, static_url_path: Optional[str] = None,
                 static_folder: Optional[str] = None, template_folder: Optional[str] = None,
                 instance_relative_config: bool = False, root_path: Optional[str] = None):
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
        self.url_map = {}
        
        # Jinja environment (placeholder for template support)
        self.jinja_env = None
        
        # Initialize Rust backend
        self._rust_app = None
        self._init_rust_backend()

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
            endpoint = options.pop('endpoint', f.__name__)
            methods = options.pop('methods', ['GET'])
            
            # Store view function
            self._view_functions[endpoint] = f
            
            # Register with Rust backend
            for method in methods:
                if inspect.iscoroutinefunction(f):
                    # Async handler
                    self._rust_app.add_async_route(method, rule, self._wrap_async_handler(f))
                else:
                    # Sync handler
                    self._rust_app.add_route(method, rule, self._wrap_sync_handler(f))
            
            return f
        return decorator

    def get(self, rule: str, **options) -> Callable:
        """Convenience decorator for GET routes."""
        return self.route(rule, methods=['GET'], **options)

    def post(self, rule: str, **options) -> Callable:
        """Convenience decorator for POST routes."""
        return self.route(rule, methods=['POST'], **options)

    def put(self, rule: str, **options) -> Callable:
        """Convenience decorator for PUT routes."""
        return self.route(rule, methods=['PUT'], **options)

    def delete(self, rule: str, **options) -> Callable:
        """Convenience decorator for DELETE routes."""
        return self.route(rule, methods=['DELETE'], **options)

    def patch(self, rule: str, **options) -> Callable:
        """Convenience decorator for PATCH routes."""
        return self.route(rule, methods=['PATCH'], **options)

    def head(self, rule: str, **options) -> Callable:
        """Convenience decorator for HEAD routes."""
        return self.route(rule, methods=['HEAD'], **options)

    def options(self, rule: str, **options) -> Callable:
        """Convenience decorator for OPTIONS routes."""
        return self.route(rule, methods=['OPTIONS'], **options)

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
        url_prefix = options.get('url_prefix', blueprint.url_prefix)
        
        # Store blueprint
        self.blueprints[blueprint.name] = blueprint
        
        # Register blueprint routes with the application
        for rule, endpoint, view_func, methods in blueprint.deferred_functions:
            if url_prefix:
                rule = url_prefix.rstrip('/') + '/' + rule.lstrip('/')
            
            # Create route with blueprint endpoint
            full_endpoint = f"{blueprint.name}.{endpoint}"
            self._view_functions[full_endpoint] = view_func
            
            # Register with Rust backend
            for method in methods:
                if inspect.iscoroutinefunction(view_func):
                    self._rust_app.add_async_route(method, rule, self._wrap_async_handler(view_func))
                else:
                    self._rust_app.add_route(method, rule, self._wrap_sync_handler(view_func))

    def _wrap_sync_handler(self, handler: Callable) -> Callable:
        """Wrap synchronous handler with request context and middleware."""
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
                
                # Call the actual handler (Flask-style handlers don't take request as param)
                result = handler()
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

    def _wrap_async_handler(self, handler: Callable) -> Callable:
        """Wrap asynchronous handler with request context and middleware."""
        @wraps(handler)
        async def wrapper(rust_request):
            try:
                # Convert Rust request to Python Request object
                request = Request._from_rust_request(rust_request)
                
                # Set request context
                _request_ctx.set(request)
                
                # Run before request handlers
                for before_func in self.before_request_funcs:
                    if inspect.iscoroutinefunction(before_func):
                        result = await before_func()
                    else:
                        result = before_func()
                    if result is not None:
                        return self._response_to_rust_format(self._make_response(result))
                
                # Call the actual handler (Flask-style handlers don't take request as param)
                if inspect.iscoroutinefunction(handler):
                    result = await handler()
                else:
                    result = handler()
                response = self._make_response(result)
                
                # Run after request handlers
                for after_func in self.after_request_funcs:
                    if inspect.iscoroutinefunction(after_func):
                        response = await after_func(response) or response
                    else:
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
                        if inspect.iscoroutinefunction(teardown_func):
                            await teardown_func(None)
                        else:
                            teardown_func(None)
                    except Exception:
                        pass
                
                # Clear request context
                _request_ctx.set(None)
        
        return wrapper

    def _make_response(self, result: Any) -> Response:
        """Convert various return types to Response objects."""
        return make_response(result)

    def _handle_exception(self, exception: Exception) -> Response:
        """Handle exceptions and return appropriate error responses."""
        # Check for registered error handlers
        for exc_class_or_code, handler in self.error_handler_spec.items():
            if isinstance(exc_class_or_code, type) and isinstance(exception, exc_class_or_code):
                return self._make_response(handler(exception))
            elif isinstance(exc_class_or_code, int):
                # For HTTP status code handlers, need to check if it matches
                # This is a simplified implementation
                pass
        
        # Default error response
        if hasattr(exception, 'code'):
            status = getattr(exception, 'code', 500)
        else:
            status = 500
            
        return Response(f"Internal Server Error: {str(exception)}", status=status)

    def _response_to_rust_format(self, response: Response) -> tuple:
        """Convert Python Response object to format expected by Rust."""
        # Return (body, status_code, headers) tuple
        headers_dict = {}
        if hasattr(response, 'headers') and response.headers:
            headers_dict = dict(response.headers)
        
        body = response.get_data(as_text=False) if hasattr(response, 'get_data') else str(response).encode('utf-8')
        status_code = response.status_code if hasattr(response, 'status_code') else 200
        
        return (body.decode('utf-8', errors='replace'), status_code, headers_dict)

    def run(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = False, 
            load_dotenv: bool = True, **options) -> None:
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
            self.config['DEBUG'] = True
            
        try:
            self._rust_app.run(host, port)
        except KeyboardInterrupt:
            print("\nShutting down server...")
        except Exception as e:
            print(f"Server error: {e}")

    async def run_async(self, host: str = '127.0.0.1', port: int = 5000, 
                       debug: bool = False, **options) -> None:
        """
        Run the application server asynchronously.
        
        Args:
            host: Hostname to bind to
            port: Port to bind to
            debug: Enable debug mode
            **options: Additional server options
        """
        if debug:
            self.config['DEBUG'] = True
            
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

    def app_context(self):
        """
        Create an application context.
        
        Returns:
            Application context manager
        """
        # Placeholder for application context implementation
        return _AppContext(self)

    def request_context(self, environ_or_request):
        """
        Create a request context.
        
        Args:
            environ_or_request: WSGI environ dict or Request object
            
        Returns:
            Request context manager
        """
        # Placeholder for request context implementation
        return _RequestContext(self, environ_or_request)


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