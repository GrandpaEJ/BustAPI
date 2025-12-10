from typing import Callable, List, Optional

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
        self._middlewares: List[Middleware] = []

    @property
    def middlewares(self) -> List[Middleware]:
        return self._middlewares

    def add(self, middleware: Middleware):
        """Add a middleware instance to the chain."""
        self._middlewares.append(middleware)

    def process_request(self, request: Request) -> Optional[Response]:
        """Run process_request on all middleware."""
        for middleware in self._middlewares:
            response = middleware.process_request(request)
            if response:
                return response
        return None

    def process_response(self, request: Request, response: Response) -> Response:
        """Run process_response on all middleware (reversed order)."""
        for middleware in reversed(self._middlewares):
            response = middleware.process_response(request, response)
        return response
