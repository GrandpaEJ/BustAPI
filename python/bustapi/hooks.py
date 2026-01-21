"""
Hook decorators and lifecycle management for BustAPI.
"""

from typing import Callable, Type, Union


class HooksMixin:
    """Mixin providing request lifecycle hooks and error handlers."""

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

    def preprocess_request(self):
        """Preprocess request - runs before_request functions."""
        for func in self.before_request_funcs:
            result = func()
            if result is not None:
                return result

    def process_response(self, response):
        """Process response - runs after_request functions."""
        for func in self.after_request_funcs:
            response = func(response)
        return response

    def do_teardown_request(self, exc=None):
        """Teardown request - runs teardown_request functions."""
        for func in self.teardown_request_funcs:
            func(exc)

    def do_teardown_appcontext(self, exc=None):
        """Teardown app context - runs teardown_appcontext functions."""
        for func in self.teardown_appcontext_funcs:
            func(exc)

    def make_default_options_response(self):
        """Make default OPTIONS response."""
        from .http.response import Response

        return Response("", 200, {"Allow": "GET,HEAD,POST,OPTIONS"})
