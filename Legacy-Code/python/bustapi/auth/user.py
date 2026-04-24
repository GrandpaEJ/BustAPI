"""
User base classes for authentication.

Provides mixins for user objects with sensible defaults.
"""

from typing import Any, Optional


class BaseUser:
    """
    Mixin for user objects. Provides default implementations.

    Usage:
        class User(db.Model, BaseUser):
            id = Column(Integer, primary_key=True)
            email = Column(String)
            password_hash = Column(String)
            active = Column(Boolean, default=True)

            def get_id(self):
                return str(self.id)
    """

    @property
    def is_authenticated(self) -> bool:
        """User is authenticated (not anonymous)."""
        return True

    @property
    def is_active(self) -> bool:
        """User account is active."""
        return True

    @property
    def is_anonymous(self) -> bool:
        """Not an anonymous user."""
        return False

    def get_id(self) -> str:
        """
        Return unique identifier for user.

        Override this if your user ID is not 'id'.
        """
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError(
                "No `id` attribute - override `get_id()`"
            ) from None


class AnonUser:
    """
    Default anonymous user when no user is logged in.

    current_user returns this when not authenticated.
    """

    @property
    def is_authenticated(self) -> bool:
        return False

    @property
    def is_active(self) -> bool:
        return False

    @property
    def is_anonymous(self) -> bool:
        return True

    def get_id(self) -> None:
        return None
