"""Tests for auth utilities (password hashing, token generation)."""

import pytest


def test_hash_password():
    """Test password hashing."""
    from bustapi import hash_password

    hashed = hash_password("mypassword123")

    assert hashed is not None
    assert isinstance(hashed, str)
    # Argon2 hash format starts with $argon2
    assert hashed.startswith("$argon2")


def test_verify_password_correct():
    """Test verifying correct password."""
    from bustapi import hash_password, verify_password

    password = "securePass!@#$"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test verifying incorrect password."""
    from bustapi import hash_password, verify_password

    hashed = hash_password("correct_password")

    assert verify_password("wrong_password", hashed) is False


def test_hash_uniqueness():
    """Test that same password produces different hashes (due to salt)."""
    from bustapi import hash_password

    hash1 = hash_password("samepassword")
    hash2 = hash_password("samepassword")

    # Hashes should be different due to random salt
    assert hash1 != hash2


def test_hash_empty_password():
    """Test hashing empty password (should work)."""
    from bustapi import hash_password, verify_password

    hashed = hash_password("")
    assert verify_password("", hashed) is True


def test_verify_invalid_hash_format():
    """Test verifying against invalid hash format."""
    from bustapi import verify_password

    with pytest.raises(ValueError, match="Invalid hash format"):
        verify_password("password", "not-a-valid-hash")


def test_generate_token():
    """Test generating secure random tokens."""
    from bustapi import generate_token

    token = generate_token()

    assert token is not None
    assert isinstance(token, str)
    # Default 32 bytes = 64 hex chars
    assert len(token) == 64


def test_generate_token_custom_length():
    """Test generating tokens of custom length."""
    from bustapi import generate_token

    token_16 = generate_token(16)
    token_64 = generate_token(64)

    assert len(token_16) == 32  # 16 bytes = 32 hex chars
    assert len(token_64) == 128  # 64 bytes = 128 hex chars


def test_generate_token_uniqueness():
    """Test that tokens are unique."""
    from bustapi import generate_token

    tokens = [generate_token() for _ in range(100)]
    unique_tokens = set(tokens)

    assert len(unique_tokens) == 100


def test_generate_csrf_token():
    """Test CSRF token generation."""
    from bustapi import generate_csrf_token

    token = generate_csrf_token()

    assert token is not None
    assert isinstance(token, str)
    assert len(token) == 64  # 32 bytes = 64 hex chars


def test_token_hex_format():
    """Test that tokens are valid hex strings."""
    from bustapi import generate_token

    token = generate_token()

    # Should only contain hex characters
    assert all(c in "0123456789abcdef" for c in token)
