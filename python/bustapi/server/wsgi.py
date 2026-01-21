"""
WSGI and ASGI adapters for BustAPI.
"""

from functools import partial
from http import HTTPStatus


class WSGIAdapter:
    """Mixin providing WSGI and ASGI compatibility."""

    def wsgi_app(self, environ, start_response):
        """
        WSGI compatibility entry point.
        """
        path = environ.get("PATH_INFO", "")
        method = environ.get("REQUEST_METHOD", "GET")
        query_string = environ.get("QUERY_STRING", "")

        # Read headers
        headers = {}
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-").lower()
                headers[header_name] = value
            elif key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                header_name = key.replace("_", "-").lower()
                headers[header_name] = value

        # Read body
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            content_length = 0

        body = b""
        if content_length > 0:
            stream = environ.get("wsgi.input")
            if stream:
                body = stream.read(content_length)

        # Call Rust backend
        body_str, status_code, headers_map = self._rust_app.handle_request(
            method, path, query_string, headers, body
        )

        # Convert status code to string
        status_line = f"{status_code} {self._get_status_text(status_code)}"

        # Convert headers
        response_headers = list(headers_map.items())

        start_response(status_line, response_headers)
        return [body_str.encode("utf-8")]

    def _get_status_text(self, code):
        """Get HTTP status text for code."""
        try:
            return HTTPStatus(code).phrase
        except ValueError:
            return "UNKNOWN"

    async def asgi_app(self, scope, receive, send):
        """
        ASGI compatibility entry point.
        """
        if scope["type"] != "http":
            return

        path = scope.get("path", "")
        method = scope.get("method", "GET")
        query_string = scope.get("query_string", b"").decode("utf-8")

        # Parse headers
        headers = {}
        for k, v in scope.get("headers", []):
            headers[k.decode("utf-8").lower()] = v.decode("utf-8")

        # Read body
        body = b""
        more_body = True
        while more_body:
            message = await receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        # Run in executor to avoid blocking
        import asyncio

        loop = asyncio.get_running_loop()

        body_str, status_code, headers_map = await loop.run_in_executor(
            None,
            partial(
                self._rust_app.handle_request, method, path, query_string, headers, body
            ),
        )

        # Send response start
        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": [
                    (k.encode("utf-8"), v.encode("utf-8"))
                    for k, v in headers_map.items()
                ],
            }
        )

        # Send response body
        await send(
            {
                "type": "http.response.body",
                "body": body_str.encode("utf-8"),
            }
        )

    def __call__(self, scope_or_environ, start_response=None, send=None):
        """
        Dual-mode dispatch: behaves like WSGI if 2 args, ASGI if 3.
        """
        if send is None and callable(start_response):
            # WSGI
            return self.wsgi_app(scope_or_environ, start_response)
        else:
            # For ASGI, users should use app.asgi_app directly
            return self.wsgi_app(scope_or_environ, start_response)
