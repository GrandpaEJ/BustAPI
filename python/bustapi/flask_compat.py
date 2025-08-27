"""
Flask compatibility layer for BustAPI

This module provides Flask class as an alias for BustAPI to enable drop-in replacement.
"""

from .app import BustAPI


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


# Re-export commonly used Flask items for compatibility
from .request import request
from .response import jsonify, make_response, Response
from .helpers import abort, redirect, url_for, render_template, render_template_string
from .helpers import flash, get_flashed_messages, send_file, send_from_directory
from .exceptions import HTTPException
from .blueprints import Blueprint

__all__ = [
    'Flask',
    'request', 
    'jsonify',
    'make_response',
    'Response',
    'abort',
    'redirect', 
    'url_for',
    'render_template',
    'render_template_string',
    'flash',
    'get_flashed_messages',
    'send_file',
    'send_from_directory',
    'HTTPException',
    'Blueprint',
]