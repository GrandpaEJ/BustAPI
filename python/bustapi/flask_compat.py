"""
Flask compatibility layer for BustAPI

This module provides Flask class as an alias for BustAPI to enable drop-in replacement.
"""

from .app import BustAPI
from .blueprints import Blueprint
from .exceptions import HTTPException
from .helpers import (
    abort,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    render_template_string,
    send_file,
    send_from_directory,
    url_for,
)
from .request import request
from .response import Response, jsonify, make_response


class Flask(BustAPI):
    """
    Flask compatibility class - direct alias for BustAPI.

    This allows BustAPI to be used as a drop-in replacement for Flask:

    Instead of:
        from flask import Flask
        app = Flask(__name__)

    Use:
        from bustapi import Flask  # or: from bustapi.flask_compat import Flask
        app = Flask(__name__)

    All Flask functionality is available through BustAPI's implementation.
    """

    pass


__all__ = [
    "Flask",
    "request",
    "jsonify",
    "make_response",
    "Response",
    "abort",
    "redirect",
    "url_for",
    "render_template",
    "render_template_string",
    "flash",
    "get_flashed_messages",
    "send_file",
    "send_from_directory",
    "HTTPException",
    "Blueprint",
]
