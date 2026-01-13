"""
BustAPI Auth Package

Flask-Login style authentication with Rust-backed utilities.

Usage:
    from bustapi.auth import (
        LoginManager, login_user, logout_user, current_user,
        BaseUser, AnonUser,
        login_required, roles_required,
        hash_password, verify_password,
        generate_token, generate_csrf_token,
        CSRFProtect,
    )
"""

# Login management
from .login import LoginManager, current_user, login_user, logout_user

# User classes
from .user import AnonUser, BaseUser

# Decorators
from .decorators import (
    fresh_login_required,
    login_required,
    permission_required,
    roles_required,
)

# Password hashing
from .password import hash_password, verify_password

# Token generation
from .tokens import generate_csrf_token, generate_token

# CSRF protection
from .csrf import CSRFProtect

__all__ = [
    # Login
    "LoginManager",
    "login_user",
    "logout_user",
    "current_user",
    # User classes
    "BaseUser",
    "AnonUser",
    # Decorators
    "login_required",
    "fresh_login_required",
    "roles_required",
    "permission_required",
    # Password
    "hash_password",
    "verify_password",
    # Tokens
    "generate_token",
    "generate_csrf_token",
    # CSRF
    "CSRFProtect",
]
