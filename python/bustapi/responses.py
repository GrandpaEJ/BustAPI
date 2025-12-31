"""
Response type aliases for Flask/FastAPI compatibility.
"""

from typing import Any, Dict, Optional, Union

from .http.response import Response, redirect


class JSONResponse(Response):
    """
    JSON Response alias (FastAPI-compatible).
    """

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[Any] = None,
    ):
        super().__init__(response=content, status=status_code, headers=headers)
        self.content_type = media_type or "application/json"
        # Background tasks not fully integrated yet, but argument accepted for compatibility


class HTMLResponse(Response):
    """
    HTML Response alias (FastAPI-compatible).
    """

    def __init__(
        self,
        content: str,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
    ):
        super().__init__(response=content, status=status_code, headers=headers)
        self.content_type = media_type or "text/html; charset=utf-8"


class PlainTextResponse(Response):
    """
    Plain Text Response alias (FastAPI-compatible).
    """

    def __init__(
        self,
        content: str,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
    ):
        super().__init__(response=content, status=status_code, headers=headers)
        self.content_type = media_type or "text/plain; charset=utf-8"


class RedirectResponse(Response):
    """
    Redirect Response alias (FastAPI-compatible).
    """

    def __init__(
        self,
        url: str,
        status_code: int = 307,
        headers: Optional[Dict[str, str]] = None,
        background: Optional[Any] = None,
    ):
        # Create base redirect response
        resp = redirect(url, code=status_code)

        # Merge custom headers if any
        if headers:
            for k, v in headers.items():
                resp.headers[k] = v

        # Copy to self (hacky but works for inheritance)
        super().__init__(status=resp.status_code, headers=resp.headers)
        self.headers["Location"] = url


class FileResponse(Response):
    """
    File Response alias (FastAPI-compatible).
    """

    def __init__(
        self,
        path: str,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
        filename: Optional[str] = None,
        method: Optional[str] = None,
        content_disposition_type: str = "attachment",
    ):
        from .core.helpers import send_file

        # Create base file response
        resp = send_file(
            path,
            mimetype=media_type,
            as_attachment=True if filename else False,
            attachment_filename=filename,
        )

        # Update status if needed
        resp.status_code = status_code

        # Merge custom headers
        if headers:
            for k, v in headers.items():
                resp.headers[k] = v

        super().__init__(
            response=resp.data, status=resp.status_code, headers=resp.headers
        )
        self.content_type = resp.content_type
