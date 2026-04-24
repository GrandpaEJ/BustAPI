"""
Response handling for BustAPI - Flask-compatible response objects
"""

import json
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any, Dict, Iterable, Optional, Union
from urllib.parse import quote


class Headers(dict):
    """Minimal stub for werkzeug.datastructures.Headers"""

    def __init__(self, headers=None):
        super().__init__()
        if headers:
            self.update(headers)

    def getlist(self, key):
        val = self.get(key)
        if val is None:
            return []
        return [val] if not isinstance(val, list) else val

    def setlist(self, key, values):
        self[key] = values


ResponseType = Union[str, bytes, dict, list, tuple, "Response"]


class Response:
    """
    Flask-compatible response object.

    This class represents an HTTP response and provides methods to set
    response data, status codes, and headers in a Flask-compatible way.
    """

    def __init__(
        self,
        response: Any = None,
        status: Optional[int] = None,
        headers: Optional[Union[Dict, Headers]] = None,
        mimetype: Optional[str] = None,
        content_type: Optional[str] = None,
    ):
        """
        Initialize response object.

        Args:
            response: Response data (string, bytes, dict, etc.)
            status: HTTP status code
            headers: Response headers
            mimetype: MIME type
            content_type: Content type header
        """
        self.status_code = status or 200
        self.headers = Headers(headers) if headers else Headers()

        # Set response data
        if response is not None:
            self.set_data(response)
        else:
            self.data = b""

        # Set content type
        if content_type:
            self.content_type = content_type
        elif mimetype:
            self.content_type = mimetype
        elif not self.content_type:
            self.content_type = "text/html; charset=utf-8"

    @property
    def status(self) -> str:
        """Status code and reason phrase."""
        try:
            status_obj = HTTPStatus(self.status_code)
            return f"{self.status_code} {status_obj.phrase}"
        except ValueError:
            return str(self.status_code)

    @status.setter
    def status(self, value: Union[str, int]) -> None:
        """Set status code."""
        if isinstance(value, str):
            # Parse "200 OK" format
            self.status_code = int(value.split()[0])
        else:
            self.status_code = value

    @property
    def content_type(self) -> str:
        """Content type header."""
        return self.headers.get("Content-Type", "")

    @content_type.setter
    def content_type(self, value: str) -> None:
        """Set content type header."""
        self.headers["Content-Type"] = value

    def set_data(self, data: Any) -> None:
        """
        Set response data.

        Args:
            data: Response data to set
        """
        if isinstance(data, str):
            self.data = data.encode("utf-8")
            if not self.content_type:
                self.content_type = "text/html; charset=utf-8"
        elif isinstance(data, bytes):
            self.data = data
        elif isinstance(data, (dict, list)):
            # Serialize as JSON
            self.data = json.dumps(data).encode("utf-8")
            self.content_type = "application/json"
        else:
            # Convert to string and encode
            self.data = str(data).encode("utf-8")
            if not self.content_type:
                self.content_type = "text/html; charset=utf-8"

    def get_data(self, as_text: bool = False) -> Union[bytes, str]:
        """
        Get response data.

        Args:
            as_text: Return as text instead of bytes

        Returns:
            Response data as bytes or text
        """
        if as_text:
            return self.data.decode("utf-8", errors="replace")
        return self.data

    @property
    def response(self) -> Iterable[bytes]:
        """Response data as iterable of bytes."""
        return [self.data]

    def set_cookie(
        self,
        key: str,
        value: str = "",
        max_age: Optional[int] = None,
        expires: Optional[Union[str, datetime, int]] = None,
        path: str = "/",
        domain: Optional[str] = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Optional[str] = None,
    ):
        """
        Set a cookie with URL encoding for security.

        Args:
            key: Cookie name
            value: Cookie value (will be URL-encoded)
            max_age: Maximum age in seconds
            expires: Expiration date (datetime, timestamp, or RFC 2822 string)
            path: Cookie path
            domain: Cookie domain
            secure: Secure flag (HTTPS only)
            httponly: HttpOnly flag (not accessible via JavaScript)
            samesite: SameSite attribute ('Strict', 'Lax', or 'None')
        """
        # URL encode the cookie value for security
        encoded_value = quote(value, safe="")
        cookie_parts = [f"{key}={encoded_value}"]

        if max_age is not None:
            cookie_parts.append(f"Max-Age={max_age}")

        if expires:
            # Handle different expires formats
            if isinstance(expires, datetime):
                # Convert datetime to RFC 2822 format
                expires_str = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
                cookie_parts.append(f"Expires={expires_str}")
            elif isinstance(expires, int):
                # Treat as timestamp
                dt = datetime.utcfromtimestamp(expires)
                expires_str = dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
                cookie_parts.append(f"Expires={expires_str}")
            else:
                # Assume it's already a properly formatted string
                cookie_parts.append(f"Expires={expires}")

        if path:
            cookie_parts.append(f"Path={path}")
        if domain:
            cookie_parts.append(f"Domain={domain}")
        if secure:
            cookie_parts.append("Secure")
        if httponly:
            cookie_parts.append("HttpOnly")
        if samesite:
            # Validate and capitalize SameSite value
            if samesite.lower() in ("strict", "lax", "none"):
                cookie_parts.append(f"SameSite={samesite.capitalize()}")

        cookie_string = "; ".join(cookie_parts)

        # Add to existing Set-Cookie headers (support multiple cookies)
        if "Set-Cookie" in self.headers:
            existing = self.headers.getlist("Set-Cookie")
            existing.append(cookie_string)
            self.headers.setlist("Set-Cookie", existing)
        else:
            self.headers["Set-Cookie"] = cookie_string

    def delete_cookie(
        self,
        key: str,
        path: str = "/",
        domain: Optional[str] = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Optional[str] = None,
    ):
        """
        Delete a cookie by setting it to expire immediately.

        Args:
            key: Cookie name to delete
            path: Cookie path (must match the path used when setting)
            domain: Cookie domain (must match the domain used when setting)
            secure: Secure flag (must match the flag used when setting)
            httponly: HttpOnly flag (must match the flag used when setting)
            samesite: SameSite attribute (must match the attribute used when setting)

        Note:
            All attributes must match those used when setting the cookie
            for the deletion to work properly.
        """
        self.set_cookie(
            key=key,
            value="",
            max_age=0,
            expires=datetime.utcnow() - timedelta(days=1),
            path=path,
            domain=domain,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
        )

    def __repr__(self) -> str:
        return f"<Response {self.status_code} [{self.content_type}]>"


def make_response(*args) -> Response:
    """
    Create a Response object from various input types (Flask-compatible).

    Args:
        *args: Response arguments - can be:
            - (response,)
            - (response, status)
            - (response, headers)
            - (response, status, headers)

    Returns:
        Response object
    """
    if not args:
        return Response()

    if len(args) == 1:
        rv = args[0]
        if isinstance(rv, Response):
            return rv
        return Response(rv)

    if len(args) == 2:
        rv, status_or_headers = args
        if isinstance(status_or_headers, (int, str)):
            # (response, status)
            return Response(rv, status=status_or_headers)
        else:
            # (response, headers)
            return Response(rv, headers=status_or_headers)

    if len(args) == 3:
        # (response, status, headers)
        rv, status, headers = args
        return Response(rv, status=status, headers=headers)

    raise TypeError(f"make_response() takes 1 to 3 arguments ({len(args)} given)")


def jsonify(*args, **kwargs) -> Response:
    """
    Create a JSON response (Flask-compatible).

    Args:
        *args: Positional arguments for JSON data
        **kwargs: Keyword arguments for JSON data

    Returns:
        Response object with JSON data

    Examples:
        jsonify({'key': 'value'})
        jsonify(key='value')
        jsonify([1, 2, 3])
    """
    if args and kwargs:
        raise TypeError("jsonify() behavior with mixed arguments is deprecated")

    if args:
        if len(args) == 1:
            data = args[0]
        else:
            data = args
    else:
        data = kwargs

    response = Response()
    response.set_data(data)
    response.content_type = "application/json"

    return response


def textify(text: str, status: int = 200) -> Response:
    """
    Create a plain text response.

    Args:
        text: Text content
        status: HTTP status code

    Returns:
        Response object with text data
    """
    response = Response(text, status=status)
    response.content_type = "text/plain; charset=utf-8"
    return response


def xmlify(xml_content: str, status: int = 200) -> Response:
    """
    Create an XML response.

    Args:
        xml_content: XML content string
        status: HTTP status code

    Returns:
        Response object with XML data
    """
    response = Response(xml_content, status=status)
    response.content_type = "application/xml; charset=utf-8"
    return response


def htmlify(html_content: str, status: int = 200) -> Response:
    """
    Create an HTML response.

    Args:
        html_content: HTML content string
        status: HTTP status code

    Returns:
        Response object with HTML data
    """
    response = Response(html_content, status=status)
    response.content_type = "text/html; charset=utf-8"
    return response


# HTTP status code helpers
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
    from ..core.exceptions import HTTPException

    raise HTTPException(code, description=description)


class HTTPException(Exception):
    """HTTP exception for error responses."""

    def __init__(self, code: int, description: Optional[str] = None):
        self.code = code
        self.description = description or self._get_default_description(code)
        super().__init__(self.description)

    def _get_default_description(self, code: int) -> str:
        """Get default description for HTTP status code."""
        try:
            return HTTPStatus(code).phrase
        except ValueError:
            return f"HTTP {code}"

    def get_response(self) -> Response:
        """Get response object for this exception."""
        return Response(self.description, status=self.code)


# Common HTTP exceptions
class BadRequest(HTTPException):
    def __init__(self, description: Optional[str] = None):
        super().__init__(400, description)


class Unauthorized(HTTPException):
    def __init__(self, description: Optional[str] = None):
        super().__init__(401, description)


class Forbidden(HTTPException):
    def __init__(self, description: Optional[str] = None):
        super().__init__(403, description)


class NotFound(HTTPException):
    def __init__(self, description: Optional[str] = None):
        super().__init__(404, description)


class MethodNotAllowed(HTTPException):
    def __init__(self, description: Optional[str] = None):
        super().__init__(405, description)


class InternalServerError(HTTPException):
    def __init__(self, description: Optional[str] = None):
        super().__init__(500, description)


# Redirect response
def redirect(location: str, code: int = 302, Response: type = Response) -> Response:
    """
    Create a redirect response.

    Args:
        location: Redirect URL
        code: HTTP status code (301, 302, etc.)
        Response: Response class to use

    Returns:
        Redirect response
    """
    response = Response("", status=code)
    response.headers["Location"] = location
    return response


# Static response helpers
def send_file(
    file_path: str,
    mimetype: Optional[str] = None,
    as_attachment: bool = False,
    attachment_filename: Optional[str] = None,
):
    """
    Send a file as response with HTTP Range support (Flask-compatible).

    Args:
        file_path: Path to file
        mimetype: MIME type
        as_attachment: Send as attachment
        attachment_filename: Attachment filename

    Returns:
        FileResponse object with Range support

    Note:
        This now returns a FileResponse which is handled by the Rust backend
        with full HTTP Range support for video streaming.
    """
    # Import here to avoid circular dependency
    from ..responses import FileResponse

    # Determine filename for attachment
    filename = None
    if as_attachment:
        filename = attachment_filename or file_path.split("/")[-1]

    # Return FileResponse which will be handled by Rust with Range support
    return FileResponse(
        path=file_path,
        media_type=mimetype,
        filename=filename,
        content_disposition_type="attachment" if as_attachment else "inline",
    )
