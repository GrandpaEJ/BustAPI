"""
Helper functions for BustAPI - Flask-compatible utilities
"""

import os
from typing import Any, Optional

from .exceptions import HTTPException
from .response import Response
from .response import redirect as _redirect


def abort(code: int, description: Optional[str] = None, **kwargs) -> None:
    """
    Abort request with HTTP error code (Flask-compatible).

    Args:
        code: HTTP status code
        description: Error description
        **kwargs: Additional arguments

    Raises:
        HTTPException: HTTP exception with specified code
    """
    raise HTTPException(code, description=description)


def redirect(location: str, code: int = 302) -> Response:
    """
    Create a redirect response (Flask-compatible).

    Args:
        location: Redirect URL
        code: HTTP status code (301, 302, etc.)

    Returns:
        Redirect response
    """
    return _redirect(location, code)


def url_for(endpoint: str, **values) -> str:
    """
    Generate URL for endpoint (Flask-compatible placeholder).

    Args:
        endpoint: Endpoint name
        **values: URL parameters

    Returns:
        Generated URL

    Note:
        This is a simplified implementation. Full URL generation
        requires route reversal which should be implemented in
        the Rust backend for performance.
    """
    # Placeholder implementation
    # TODO: Implement proper URL reversal with route mapping

    # For now, just return the endpoint as-is
    # In a full implementation, this would:
    # 1. Look up the route pattern for the endpoint
    # 2. Substitute parameters into the pattern
    # 3. Generate the full URL

    if values:
        # Simple parameter substitution for basic cases
        url = endpoint
        for key, value in values.items():
            url = url.replace(f"<{key}>", str(value))
            url = url.replace(f"<int:{key}>", str(value))
            url = url.replace(f"<string:{key}>", str(value))
        return url

    return endpoint


def flash(message: str, category: str = "message") -> None:
    """
    Flash a message to the user (Flask-compatible placeholder).

    Args:
        message: Message to flash
        category: Message category

    Note:
        This is a placeholder implementation. Flash messaging
        requires session support which should be implemented.
    """
    # TODO: Implement flash messaging with session support
    pass


def get_flashed_messages(
    with_categories: bool = False, category_filter: Optional[list] = None
) -> list:
    """
    Get flashed messages (Flask-compatible placeholder).

    Args:
        with_categories: Include categories in result
        category_filter: Filter by categories

    Returns:
        List of flashed messages

    Note:
        This is a placeholder implementation.
    """
    # TODO: Implement flash message retrieval
    return []


def send_file(
    path_or_file,
    mimetype: Optional[str] = None,
    as_attachment: bool = False,
    attachment_filename: Optional[str] = None,
    add_etags: bool = True,
    cache_timeout: Optional[int] = None,
    conditional: bool = False,
    last_modified: Optional[Any] = None,
) -> Response:
    """
    Send a file to the user (Flask-compatible).

    Args:
        path_or_file: File path or file-like object
        mimetype: MIME type
        as_attachment: Send as attachment
        attachment_filename: Attachment filename
        add_etags: Add ETag header
        cache_timeout: Cache timeout
        conditional: Enable conditional responses
        last_modified: Last modified time

    Returns:
        Response object with file content
    """
    from .response import send_file as _send_file

    return _send_file(path_or_file, mimetype, as_attachment, attachment_filename)


def send_from_directory(directory: str, path: str, **kwargs) -> Response:
    """
    Send a file from a directory (Flask-compatible).

    Args:
        directory: Directory path
        path: File path within directory
        **kwargs: Additional arguments for send_file

    Returns:
        Response object with file content
    """
    # Security: ensure path doesn't escape directory
    safe_path = os.path.normpath(path).lstrip("/")
    full_path = os.path.join(directory, safe_path)

    # Check if path tries to escape directory
    if not os.path.abspath(full_path).startswith(os.path.abspath(directory)):
        abort(404, description="File not found")

    return send_file(full_path, **kwargs)


def safe_join(directory: str, *pathnames: str) -> Optional[str]:
    """
    Safely join directory and path components.

    Args:
        directory: Base directory
        *pathnames: Path components to join

    Returns:
        Joined path or None if unsafe
    """
    if not pathnames:
        return directory

    path = os.path.join(directory, *pathnames)
    path = os.path.normpath(path)

    # Check if path tries to escape directory
    if not path.startswith(directory + os.sep) and path != directory:
        return None

    return path


def escape(text: str) -> str:
    """
    Escape HTML special characters.

    Args:
        text: Text to escape

    Returns:
        Escaped text
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def get_debug_flag() -> bool:
    """
    Get debug flag from environment or current app.

    Returns:
        Debug flag value
    """
    # Check environment variable first
    debug_env = os.environ.get("FLASK_DEBUG", "").lower()
    if debug_env in ("1", "true", "yes", "on"):
        return True
    elif debug_env in ("0", "false", "no", "off"):
        return False

    # Try to get from current app
    try:
        current_app = _get_current_object()
        return current_app.config.get("DEBUG", False)
    except RuntimeError:
        return False


def _get_current_object():
    """
    Get current application object (placeholder).

    Returns:
        Current application

    Raises:
        RuntimeError: If no application context
    """
    # TODO: Implement application context
    raise RuntimeError("Working outside of application context")


# Template helpers (placeholders)
def render_template(template_name: str, **context) -> str:
    """
    Render template (Flask-compatible placeholder).

    Args:
        template_name: Template filename
        **context: Template context variables

    Returns:
        Rendered template string

    Note:
        This is a placeholder. Template rendering should be
        implemented with a proper template engine like Jinja2.
    """
    # TODO: Implement template rendering
    return f"<!-- Template: {template_name} -->"


def render_template_string(source: str, **context) -> str:
    """
    Render template from string (Flask-compatible placeholder).

    Args:
        source: Template source string
        **context: Template context variables

    Returns:
        Rendered template string
    """
    # TODO: Implement template rendering from string
    return source


# JSON helpers
def jsonify(*args, **kwargs) -> Response:
    """
    Create JSON response (re-export from response module).

    Args:
        *args: Positional arguments for JSON data
        **kwargs: Keyword arguments for JSON data

    Returns:
        JSON response
    """
    from .response import jsonify as _jsonify

    return _jsonify(*args, **kwargs)


# Request helpers
def get_json() -> Any:
    """
    Get JSON data from current request.

    Returns:
        JSON data from request
    """
    from .request import request

    return request.get_json()


# URL helpers
def url_quote(string: str, charset: str = "utf-8", safe: str = "/:") -> str:
    """
    URL quote a string.

    Args:
        string: String to quote
        charset: Character encoding
        safe: Characters to not quote

    Returns:
        URL quoted string
    """
    from urllib.parse import quote

    if isinstance(string, str):
        string = string.encode(charset)
    return quote(string, safe=safe)


def url_unquote(string: str, charset: str = "utf-8") -> str:
    """
    URL unquote a string.

    Args:
        string: String to unquote
        charset: Character encoding

    Returns:
        URL unquoted string
    """
    from urllib.parse import unquote

    return unquote(string, encoding=charset)


# Configuration helpers
def get_env() -> str:
    """
    Get environment name.

    Returns:
        Environment name (development, production, etc.)
    """
    return os.environ.get("FLASK_ENV", "development")


def get_load_dotenv(default: bool = True) -> bool:
    """
    Check if .env files should be loaded.

    Args:
        default: Default value

    Returns:
        Whether to load .env files
    """
    return os.environ.get("FLASK_SKIP_DOTENV", "").lower() not in ("1", "true", "yes")
