from typing import Callable, Optional

from .http.request import Request
from .http.response import Response


class Middleware:
    """
    Base class for BustAPI middleware.
    """

    def process_request(self, request: Request) -> Optional[Response]:
        """
        Called before the view function.

        Args:
            request: The incoming request object

        Returns:
            None to continue processing, or a Response object to stop invalid processing
            and return the response immediately.
        """
        return None

    def process_response(self, request: Request, response: Response) -> Response:
        """
        Called after the view function.

        Args:
            request: The request object
            response: The response object produced by the view or previous middleware

        Returns:
            A Response object (modified or original).
        """
        return response


class MiddlewareManager:
    """
    Manages the execution of middleware chains.
    """

    def __init__(self):
        self._middleware = []

    def add(self, middleware: Middleware):
        """Add a middleware instance to the chain."""
        self._middleware.append(middleware)

    def process_request(self, request: Request) -> Optional[Response]:
        """Run process_request on all middleware."""
        for md in self._middleware:
            response = md.process_request(request)
            if response is not None:
                return response
        return None

    def process_response(self, request: Request, response: Response) -> Response:
        """Run process_response on all middleware (in reverse order)."""
        for md in reversed(self._middleware):
            response = md.process_response(request, response)
        return response
