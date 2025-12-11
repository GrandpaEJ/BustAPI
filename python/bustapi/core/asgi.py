import asyncio
import inspect
from typing import TYPE_CHECKING

from ..dispatch import create_async_wrapper, create_sync_wrapper
from ..http.request import Request

if TYPE_CHECKING:
    from ..app import BustAPI


class BustAPIAsgiWrapper:
    """
    ASGI Adapter for BustAPI.
    """

    def __init__(self, app: "BustAPI"):
        self.app = app

    async def __call__(self, scope, receive, send):
        """Standard ASGI entry point."""
        if scope["type"] != "http":
            return

        method = scope.get("method", "GET")
        path = scope.get("path", "/")

        # 1. Match Route (Python-side)
        import re

        handler = None
        matched_rule = None

        for rule, rule_info in self.app.url_map.items():
            allowed_methods = rule_info.get("methods", ["GET"])
            allowed_methods = [m.upper() for m in allowed_methods]
            if method not in allowed_methods and method != "OPTIONS":
                continue

            regex_rule = re.sub(r"<([^>]+)>", r"(?P<\1>[^/]+)", rule)
            regex_rule = f"^{regex_rule}$"

            match = re.match(regex_rule, path)
            if match:
                matched_rule = rule
                endpoint = rule_info["endpoint"]
                handler = self.app.view_functions.get(endpoint)
                break

        if not handler:
            await send(
                {
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [(b"content-type", b"text/plain")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b"Not Found",
                }
            )
            return

        # 2. Mock Rust Request
        # Read body
        body = b""
        more_body = True
        while more_body:
            message = await receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        class MockRustRequest:
            def __init__(self, scope, body):
                self.method = method
                self.path = path
                self.headers = {}
                for k, v in scope.get("headers", []):
                    self.headers[k.decode("latin1")] = v.decode("latin1")

                self.body = body
                self.args = {}
                # Query string parsing
                qs = scope.get("query_string", b"").decode("utf-8")
                if qs:
                    from urllib.parse import parse_qs

                    parsed = parse_qs(qs)
                    for k, v in parsed.items():
                        self.args[k] = v[0]

            def get_data(self):
                return self.body

        mock_request = MockRustRequest(scope, body)

        # 3. Call Wrapped Handler
        if inspect.iscoroutinefunction(handler):
            # Native async
            wrapper = create_async_wrapper(self.app, handler, matched_rule)
            result = await wrapper(mock_request)
        else:
            # Sync handler run in threadpool?
            # For now run sync (blocking event loop - bad but functional for adapter)
            # Or use sync_to_async
            wrapper = create_sync_wrapper(self.app, handler, matched_rule)
            result = wrapper(mock_request)

        # result is (body, status, headers)
        body_resp, status_code, headers_resp = result

        # 4. Send Response
        headers_list = [
            (k.encode("utf-8"), str(v).encode("utf-8")) for k, v in headers_resp.items()
        ]

        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": headers_list,
            }
        )

        if isinstance(body_resp, str):
            data = body_resp.encode("utf-8")
        elif isinstance(body_resp, bytes):
            data = body_resp
        else:
            data = str(body_resp).encode("utf-8")

        await send(
            {
                "type": "http.response.body",
                "body": data,
            }
        )
