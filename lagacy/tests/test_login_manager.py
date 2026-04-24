"""Tests for LoginManager and session-based authentication."""

import pytest


def test_base_user_defaults():
    """Test BaseUser default properties."""
    from bustapi.auth import BaseUser

    class User(BaseUser):
        def __init__(self, id):
            self.id = id

    user = User(123)
    assert user.is_authenticated is True
    assert user.is_active is True
    assert user.is_anonymous is False
    assert user.get_id() == "123"


def test_anon_user_defaults():
    """Test AnonUser default properties."""
    from bustapi.auth import AnonUser

    anon = AnonUser()
    assert anon.is_authenticated is False
    assert anon.is_active is False
    assert anon.is_anonymous is True
    assert anon.get_id() is None


def test_login_manager_creation():
    """Test LoginManager can be created."""
    from bustapi.auth import LoginManager

    lm = LoginManager()
    assert lm is not None
    assert lm._user_loader_callback is None


def test_login_manager_user_loader_decorator():
    """Test user_loader decorator registers callback."""
    from bustapi.auth import LoginManager

    lm = LoginManager()

    @lm.user_loader
    def load_user(user_id):
        return {"id": user_id}

    assert lm._user_loader_callback is not None
    assert lm._user_loader_callback("123") == {"id": "123"}


def test_login_manager_config():
    """Test LoginManager configuration options."""
    from bustapi.auth import LoginManager

    lm = LoginManager()
    lm.login_view = "auth.login"
    lm.login_message = "Please login first"

    assert lm.login_view == "auth.login"
    assert lm.login_message == "Please login first"


def test_imports_from_bustapi():
    """Test all auth exports are available from bustapi."""
    from bustapi import (
        AnonUser,
        BaseUser,
        CSRFProtect,
        LoginManager,
        current_user,
        fresh_login_required,
        generate_csrf_token,
        generate_token,
        hash_password,
        login_required,
        login_user,
        logout_user,
        permission_required,
        roles_required,
        verify_password,
    )

    # All imports should work
    assert LoginManager is not None
    assert login_user is not None
    assert logout_user is not None
    assert current_user is not None
    assert BaseUser is not None
    assert AnonUser is not None
    assert login_required is not None
    assert fresh_login_required is not None
    assert roles_required is not None
    assert permission_required is not None
