"""
Utility classes and functions for BustAPI.
"""

from typing import Any, Callable


class LocalProxy:
    """
    A proxy to a local object, similar to werkzeug.local.LocalProxy.
    Forwards operations to the object returned by the bound function.
    """

    __slots__ = ("_local", "__wrapped__")

    def __init__(self, local: Callable[[], Any]):
        object.__setattr__(self, "_local", local)

    def _get_current_object(self) -> Any:
        """Get the currently bound object."""
        return object.__getattribute__(self, "_local")()

    @property
    def __dict__(self):
        try:
            return self._get_current_object().__dict__
        except RuntimeError:
            raise AttributeError("__dict__") from None

    def __getattr__(self, name: str) -> Any:
        return getattr(self._get_current_object(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._get_current_object(), name, value)

    def __delattr__(self, name: str) -> None:
        delattr(self._get_current_object(), name)

    def __repr__(self) -> str:
        try:
            obj = self._get_current_object()
        except RuntimeError:
            return "<LocalProxy unbound>"
        return repr(obj)

    def __str__(self) -> str:
        try:
            return str(self._get_current_object())
        except RuntimeError:
            return "<LocalProxy unbound>"

    def __bool__(self) -> bool:
        try:
            return bool(self._get_current_object())
        except RuntimeError:
            return False

    def __dir__(self):
        try:
            return dir(self._get_current_object())
        except RuntimeError:
            return []

    def __eq__(self, other: Any) -> bool:
        try:
            return self._get_current_object() == other
        except RuntimeError:
            return False

    def __ne__(self, other: Any) -> bool:
        try:
            return self._get_current_object() != other
        except RuntimeError:
            return True

    def __hash__(self) -> int:
        return hash(self._get_current_object())
