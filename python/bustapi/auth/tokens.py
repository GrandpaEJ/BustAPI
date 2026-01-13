"""
Token generation utilities (via Rust).
"""

from ..bustapi_core import generate_csrf_token, generate_token

__all__ = ["generate_token", "generate_csrf_token"]
