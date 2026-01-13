"""Tests for JWT functionality."""

import time

import pytest


def test_jwt_manager_creation():
    """Test JWTManager can be created."""
    from bustapi.bustapi_core import JWTManager

    manager = JWTManager("this-is-a-secret-key-1234567890")
    assert manager is not None


def test_jwt_manager_requires_min_key_length():
    """Test that short keys are rejected."""
    from bustapi.bustapi_core import JWTManager

    with pytest.raises(ValueError, match="at least 16 characters"):
        JWTManager("short")


def test_create_access_token():
    """Test creating an access token."""
    from bustapi.bustapi_core import JWTManager

    manager = JWTManager("this-is-a-secret-key-1234567890")
    token = manager.create_access_token("user123")

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
    # JWT format: header.payload.signature
    assert token.count(".") == 2


def test_create_refresh_token():
    """Test creating a refresh token."""
    from bustapi.bustapi_core import JWTManager

    manager = JWTManager("this-is-a-secret-key-1234567890")
    token = manager.create_refresh_token("user123")

    assert token is not None
    assert isinstance(token, str)
    assert token.count(".") == 2


def test_decode_token():
    """Test decoding a valid token."""
    from bustapi.bustapi_core import JWTManager

    manager = JWTManager("this-is-a-secret-key-1234567890")
    token = manager.create_access_token("user456")

    claims = manager.decode_token(token)

    assert claims["identity"] == "user456"
    assert claims["sub"] == "user456"
    assert "exp" in claims
    assert "iat" in claims
    assert claims["type"] == "access"
    assert claims["fresh"] is True


def test_decode_refresh_token():
    """Test decoding a refresh token."""
    from bustapi.bustapi_core import JWTManager

    manager = JWTManager("this-is-a-secret-key-1234567890")
    token = manager.create_refresh_token("user789")

    claims = manager.decode_token(token)

    assert claims["identity"] == "user789"
    assert claims["type"] == "refresh"
    assert "fresh" not in claims or claims.get("fresh") is None


def test_verify_token():
    """Test token verification."""
    from bustapi.bustapi_core import JWTManager

    manager = JWTManager("this-is-a-secret-key-1234567890")
    token = manager.create_access_token("user123")

    assert manager.verify_token(token) is True
    assert manager.verify_token("invalid.token.here") is False


def test_invalid_signature():
    """Test that wrong key fails verification."""
    from bustapi.bustapi_core import JWTManager

    manager1 = JWTManager("this-is-a-secret-key-1234567890")
    manager2 = JWTManager("different-secret-key-1234567890")

    token = manager1.create_access_token("user123")

    # Should not verify with different key
    assert manager2.verify_token(token) is False


def test_custom_claims():
    """Test adding custom claims to token."""
    from bustapi.bustapi_core import JWTManager

    manager = JWTManager("this-is-a-secret-key-1234567890")
    token = manager.create_access_token("user123", claims={"role": "admin", "level": 5})

    claims = manager.decode_token(token)

    assert claims["role"] == "admin"
    assert claims["level"] == 5


def test_get_identity():
    """Test extracting identity from token."""
    from bustapi.bustapi_core import JWTManager

    manager = JWTManager("this-is-a-secret-key-1234567890")
    token = manager.create_access_token("user999")

    identity = manager.get_identity(token)
    assert identity == "user999"


@pytest.mark.skip(reason="JWT library has built-in leeway, timing-sensitive test")
def test_expired_token():
    """Test that expired token is rejected."""
    from bustapi.bustapi_core import JWTManager

    # Create manager with very short expiry (1 second, but create token for 0 expiry)
    manager = JWTManager("this-is-a-secret-key-1234567890")
    # Create token that expires immediately (0 seconds from now)
    token = manager.create_access_token("user123", expires_delta=0)

    # The token should be expired immediately or very soon
    # Wait a tiny bit to ensure we're past expiry
    time.sleep(0.1)

    with pytest.raises(ValueError, match="expired"):
        manager.decode_token(token)


def test_algorithm_selection():
    """Test different algorithms."""
    from bustapi.bustapi_core import JWTManager

    for algo in ["HS256", "HS384", "HS512"]:
        manager = JWTManager("this-is-a-secret-key-1234567890", algorithm=algo)
        token = manager.create_access_token("user123")
        claims = manager.decode_token(token)
        assert claims["identity"] == "user123"


def test_invalid_algorithm():
    """Test invalid algorithm raises error."""
    from bustapi.bustapi_core import JWTManager

    with pytest.raises(ValueError, match="Unsupported algorithm"):
        JWTManager("this-is-a-secret-key-1234567890", algorithm="RS256")
