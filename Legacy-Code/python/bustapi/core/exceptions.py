"""
Exception classes for BustAPI - Flask-compatible exceptions
"""

from http import HTTPStatus
from typing import Optional


class BustAPIException(Exception):
    """Base exception class for BustAPI."""

    pass


class HTTPException(BustAPIException):
    """
    HTTP exception for error responses (Flask-compatible).

    This exception is raised when an HTTP error response should be returned.
    """

    def __init__(self, code: int, description: Optional[str] = None, response=None):
        """
        Initialize HTTP exception.

        Args:
            code: HTTP status code
            description: Error description
            response: Response object
        """
        self.code = code
        self.name = self._get_name(code)
        self.description = description or self._get_default_description(code)
        self.response = response

        super().__init__(f"{self.code} {self.name}: {self.description}")

    def _get_name(self, code: int) -> str:
        """Get name for HTTP status code."""
        try:
            return HTTPStatus(code).name.replace("_", " ").title()
        except ValueError:
            return f"HTTP {code}"

    def _get_default_description(self, code: int) -> str:
        """Get default description for HTTP status code."""
        try:
            return HTTPStatus(code).phrase
        except ValueError:
            return f"HTTP Error {code}"

    def get_response(self):
        """
        Get response object for this exception.

        Returns:
            Response object
        """
        if self.response is not None:
            return self.response

        from ..http.response import Response

        return Response(self.description, status=self.code)

    def get_body(self) -> str:
        """Get response body."""
        return self.description

    def get_headers(self) -> dict:
        """Get response headers."""
        return {}


# Common HTTP exceptions (Flask-compatible)


class BadRequest(HTTPException):
    """400 Bad Request exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(400, description, response)


class Unauthorized(HTTPException):
    """401 Unauthorized exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(401, description, response)


class Forbidden(HTTPException):
    """403 Forbidden exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(403, description, response)


class NotFound(HTTPException):
    """404 Not Found exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(404, description, response)


class MethodNotAllowed(HTTPException):
    """405 Method Not Allowed exception."""

    def __init__(
        self, description: Optional[str] = None, response=None, valid_methods=None
    ):
        super().__init__(405, description, response)
        self.valid_methods = valid_methods or []

    def get_headers(self) -> dict:
        """Get response headers including Allow header."""
        headers = super().get_headers()
        if self.valid_methods:
            headers["Allow"] = ", ".join(self.valid_methods)
        return headers


class NotAcceptable(HTTPException):
    """406 Not Acceptable exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(406, description, response)


class RequestTimeout(HTTPException):
    """408 Request Timeout exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(408, description, response)


class Conflict(HTTPException):
    """409 Conflict exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(409, description, response)


class Gone(HTTPException):
    """410 Gone exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(410, description, response)


class LengthRequired(HTTPException):
    """411 Length Required exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(411, description, response)


class PreconditionFailed(HTTPException):
    """412 Precondition Failed exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(412, description, response)


class RequestEntityTooLarge(HTTPException):
    """413 Request Entity Too Large exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(413, description, response)


class RequestURITooLarge(HTTPException):
    """414 Request-URI Too Large exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(414, description, response)


class UnsupportedMediaType(HTTPException):
    """415 Unsupported Media Type exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(415, description, response)


class RequestedRangeNotSatisfiable(HTTPException):
    """416 Requested Range Not Satisfiable exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(416, description, response)


class ExpectationFailed(HTTPException):
    """417 Expectation Failed exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(417, description, response)


class ImATeapot(HTTPException):
    """418 I'm a teapot exception (RFC 2324)."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(418, description, response)


class UnprocessableEntity(HTTPException):
    """422 Unprocessable Entity exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(422, description, response)


class Locked(HTTPException):
    """423 Locked exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(423, description, response)


class FailedDependency(HTTPException):
    """424 Failed Dependency exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(424, description, response)


class PreconditionRequired(HTTPException):
    """428 Precondition Required exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(428, description, response)


class TooManyRequests(HTTPException):
    """429 Too Many Requests exception."""

    def __init__(
        self, description: Optional[str] = None, response=None, retry_after=None
    ):
        super().__init__(429, description, response)
        self.retry_after = retry_after

    def get_headers(self) -> dict:
        """Get response headers including Retry-After header."""
        headers = super().get_headers()
        if self.retry_after:
            headers["Retry-After"] = str(self.retry_after)
        return headers


class RequestHeaderFieldsTooLarge(HTTPException):
    """431 Request Header Fields Too Large exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(431, description, response)


class UnavailableForLegalReasons(HTTPException):
    """451 Unavailable For Legal Reasons exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(451, description, response)


# 5xx Server Error exceptions


class InternalServerError(HTTPException):
    """500 Internal Server Error exception."""

    def __init__(
        self, description: Optional[str] = None, response=None, original_exception=None
    ):
        super().__init__(500, description, response)
        self.original_exception = original_exception


class NotImplemented(HTTPException):
    """501 Not Implemented exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(501, description, response)


class BadGateway(HTTPException):
    """502 Bad Gateway exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(502, description, response)


class ServiceUnavailable(HTTPException):
    """503 Service Unavailable exception."""

    def __init__(
        self, description: Optional[str] = None, response=None, retry_after=None
    ):
        super().__init__(503, description, response)
        self.retry_after = retry_after

    def get_headers(self) -> dict:
        """Get response headers including Retry-After header."""
        headers = super().get_headers()
        if self.retry_after:
            headers["Retry-After"] = str(self.retry_after)
        return headers


class GatewayTimeout(HTTPException):
    """504 Gateway Timeout exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(504, description, response)


class HTTPVersionNotSupported(HTTPException):
    """505 HTTP Version Not Supported exception."""

    def __init__(self, description: Optional[str] = None, response=None):
        super().__init__(505, description, response)


# Application-specific exceptions


class ConfigurationError(BustAPIException):
    """Configuration error exception."""

    pass


class TemplateNotFound(BustAPIException):
    """Template not found exception."""

    def __init__(self, template_name: str):
        self.template_name = template_name
        super().__init__(f"Template '{template_name}' not found")


class BlueprintSetupError(BustAPIException):
    """Blueprint setup error exception."""

    pass


class SecurityError(BustAPIException):
    """Security-related error exception."""

    pass


# Utility functions


def abort(code: int, description: Optional[str] = None, **kwargs):
    """
    Abort request with HTTP error code.

    Args:
        code: HTTP status code
        description: Error description
        **kwargs: Additional arguments

    Raises:
        HTTPException: HTTP exception with specified code
    """
    # Map common status codes to specific exception classes
    exception_map = {
        400: BadRequest,
        401: Unauthorized,
        403: Forbidden,
        404: NotFound,
        405: MethodNotAllowed,
        406: NotAcceptable,
        408: RequestTimeout,
        409: Conflict,
        410: Gone,
        411: LengthRequired,
        412: PreconditionFailed,
        413: RequestEntityTooLarge,
        414: RequestURITooLarge,
        415: UnsupportedMediaType,
        416: RequestedRangeNotSatisfiable,
        417: ExpectationFailed,
        418: ImATeapot,
        422: UnprocessableEntity,
        423: Locked,
        424: FailedDependency,
        428: PreconditionRequired,
        429: TooManyRequests,
        431: RequestHeaderFieldsTooLarge,
        451: UnavailableForLegalReasons,
        500: InternalServerError,
        501: NotImplemented,
        502: BadGateway,
        503: ServiceUnavailable,
        504: GatewayTimeout,
        505: HTTPVersionNotSupported,
    }

    exception_class = exception_map.get(code, HTTPException)
    if exception_class == HTTPException:
        raise exception_class(code, description, **kwargs)
    else:
        # Filter kwargs for specific exception classes
        if code in (405, 429, 503) and "valid_methods" in kwargs:
            raise exception_class(description, **kwargs)
        else:
            raise exception_class(description)


# Exception handler registry
_exception_handlers = {}


def register_error_handler(code_or_exception, handler):
    """
    Register error handler for HTTP status code or exception.

    Args:
        code_or_exception: HTTP status code or exception class
        handler: Handler function
    """
    _exception_handlers[code_or_exception] = handler


def get_error_handler(code_or_exception):
    """
    Get error handler for HTTP status code or exception.

    Args:
        code_or_exception: HTTP status code or exception class

    Returns:
        Handler function or None
    """
    return _exception_handlers.get(code_or_exception)
