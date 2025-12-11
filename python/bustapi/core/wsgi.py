import inspect
from typing import TYPE_CHECKING

from ..dispatch import create_async_wrapper, create_sync_wrapper
from ..http.request import Request

if TYPE_CHECKING:
    from ..app import BustAPI


class BustAPIWsgiWrapper:
    """
    WSGI Adapter for BustAPI.
    Allows running the application with standard WSGI servers (Gunicorn, etc.)
    and enables Flask-compatible testing clients.
    """

    def __init__(self, app: "BustAPI"):
        self.app = app

    def __call__(self, environ, start_response):
        """Standard WSGI entry point."""
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/")

        # 1. Match Route (Simple Python-side matching)
        # Note: This is an O(N) fallback. Rust router is O(1)/O(log N).
        # We need to find the handler and the rule.

        handler = None
        matched_rule = None
        path_params = {}

        # Naive matching (should match logic in app._extract_path_params logic)
        import re

        for rule, rule_info in self.app.url_map.items():
            # Check method
            allowed_methods = rule_info.get("methods", ["GET"])
            if method not in allowed_methods and method != "OPTIONS":
                continue

            # Regex match
            # This replicates _extract_path_params logic but doing it for routing
            # <param> -> (?P<param>[^/]+)
            regex_rule = re.sub(r"<([^>]+)>", r"(?P<\1>[^/]+)", rule)
            regex_rule = f"^{regex_rule}$"

            match = re.match(regex_rule, path)
            if match:
                matched_rule = rule
                endpoint = rule_info["endpoint"]
                handler = self.app.view_functions.get(endpoint)
                path_params = match.groupdict()
                break

        if not handler:
            start_response("404 Not Found", [("Content-Type", "text/plain")])
            return [b"Not Found"]

        # 2. Mock Rust Request
        # We need to create an object that looks like PyRequest for the wrapper
        class MockRustRequest:
            def __init__(self, environ, body):
                self.method = method
                self.path = path
                self.headers = {}
                # Convert WSGI headers to dict
                for k, v in environ.items():
                    if k.startswith("HTTP_"):
                        self.headers[k[5:].replace("_", "-").lower()] = v
                    elif k in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                        self.headers[k.replace("_", "-").lower()] = v

                self.body = body  # bytes
                self.args = {}  # Query string parsing needed?
                # Simple query parsing
                self.args = {}
                qs = environ.get("QUERY_STRING", "")
                if qs:
                    from urllib.parse import parse_qs

                    parsed = parse_qs(qs)
                    # Flatten
                    for k, v in parsed.items():
                        self.args[k] = v[0]

            def get_data(self):
                return self.body

        # Read body
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            content_length = 0

        body = environ["wsgi.input"].read(content_length)
        mock_request = MockRustRequest(environ, body)

        # 3. Call Wrapped Handler
        # We need to wrap the raw handler with our dispatch logic
        # Ideally we cache this wrapper?
        if inspect.iscoroutinefunction(handler):
            # Async in WSGI? We have to run it sync.
            # create_async_wrapper handles sync execution via asyncio.run
            wrapper = create_async_wrapper(self.app, handler, matched_rule)
        else:
            wrapper = create_sync_wrapper(self.app, handler, matched_rule)

        # Execute
        result = wrapper(mock_request)

        # result is (body, status, headers)
        body_resp, status_code, headers_resp = result

        # 4. Return WSGI Response
        # Convert status code to string
        from http import HTTPStatus

        try:
            status_phrase = HTTPStatus(status_code).phrase
        except ValueError:
            status_phrase = "Unknown"
        status_str = f"{status_code} {status_phrase}"

        # Headers list
        header_list = [(k, str(v)) for k, v in headers_resp.items()]

        start_response(status_str, header_list)

        if isinstance(body_resp, str):
            return [body_resp.encode("utf-8")]
        elif isinstance(body_resp, bytes):
            return [body_resp]
        else:
            return [str(body_resp).encode("utf-8")]
