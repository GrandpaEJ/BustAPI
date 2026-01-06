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
        # Initialize base response with empty body
        super().__init__(response=None, status=status_code, headers=headers)

        # Store the path - convert to absolute if relative
        import os

        if not os.path.isabs(path):
            # If relative, make it absolute from current working directory
            self.path = os.path.abspath(path)
        else:
            self.path = path

        # Determine media type
        if media_type:
            self.content_type = media_type
        else:
            import mimetypes

            guessed_type, _ = mimetypes.guess_type(path)
            if guessed_type:
                self.content_type = guessed_type

        # Handle Content-Disposition
        if filename or content_disposition_type == "attachment":
            fname = filename or path.split("/")[-1]
            self.headers["Content-Disposition"] = (
                f"{content_disposition_type}; filename={fname}"
            )


class StreamingResponse(Response):
    """
    Streaming Response alias (FastAPI-compatible).
    """

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
    ):
        super().__init__(response=None, status=status_code, headers=headers)
        self.content = content
        self.content_type = media_type or "application/octet-stream"

        # We don't verify iterator type strictly here, Rust will handle it.
        # But we can check for async iterator to set a flag if needed.
        # For now, we trust the content is an iterator/generator.
