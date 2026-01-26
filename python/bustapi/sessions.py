import base64
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .bustapi_core import Signer
from .http.request import Request
from .http.response import Response


class SessionMixin(dict):
    """Mixin for dict-based sessions."""

    def __init__(self, initial=None):
        super().__init__(initial or {})
        self.modified = False

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.modified = True

    def __delitem__(self, key):
        super().__delitem__(key)
        self.modified = True

    def clear(self):
        super().clear()
        self.modified = True

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.modified = True

    def pop(self, key, default=None):
        val = super().pop(key, default)
        self.modified = True
        return val


class SecureCookieSession(SessionMixin):
    """Secure cookie-based session."""

    pass


class NullSession(SessionMixin):
    """Session class used when sessions are disabled or support is missing."""

    pass


class SessionInterface(ABC):
    """Base class for session interfaces."""

    @abstractmethod
    def open_session(self, app, request: Request) -> Optional[SessionMixin]:
        """Load session from request."""
        pass

    @abstractmethod
    def save_session(self, app, session: SessionMixin, response: Response) -> None:
        """Save session to response."""
        pass


class SecureCookieSessionInterface(SessionInterface):
    """Default session interface using secure cookies (Rust-backed signing)."""

    session_class = SecureCookieSession
    session_cookie_name = "session"

    def open_session(self, app, request: Request) -> Optional[SessionMixin]:
        if not app.secret_key:
            return None

        # Value from cookie (signed string)
        val = request.cookies.get(self.session_cookie_name)
        if not val:
            return self.session_class()

        signer = Signer(app.secret_key)

        # 1. Verify signature using Rust
        payload = signer.verify(self.session_cookie_name, val)
        if payload is None:
            # Invalid signature
            return self.session_class()

        # 2. Decode payload (Base64 -> JSON -> Dict)
        try:
            # We treat the payload as base64 encoded JSON to match standard practices
            # But wait, our Rust signer just signs the string we give it.
            # So we need to serialize the dict to string first.
            # Structure: Base64(JSON(session_dict))
            json_str = base64.urlsafe_b64decode(payload).decode("utf-8")
            data = json.loads(json_str)
            return self.session_class(data)
        except Exception:
            # JSON/Base64 error
            return self.session_class()

    def save_session(self, app, session: SessionMixin, response: Response) -> None:
        domain = app.config.get("SESSION_COOKIE_DOMAIN")
        path = app.config.get("SESSION_COOKIE_PATH", "/")

        # If the session is empty/modified, we might want to delete it or update it
        if not session and session.modified:
            # Delete cookie
            response.set_cookie(
                self.session_cookie_name, "", expires=0, domain=domain, path=path
            )
            return

        if not app.secret_key:
            return

        if session.modified:
            # 1. Serialize: Dict -> JSON -> Base64
            json_str = json.dumps(dict(session))
            payload = base64.urlsafe_b64encode(json_str.encode("utf-8")).decode("utf-8")

            # 2. Sign: Rust signer
            signer = Signer(app.secret_key)
            val = signer.sign(self.session_cookie_name, payload)

            response.set_cookie(
                self.session_cookie_name,
                val,
                httponly=True,
                domain=domain,
                path=path,
                secure=app.config.get("SESSION_COOKIE_SECURE", False),
                samesite=app.config.get("SESSION_COOKIE_SAMESITE", "Lax"),
            )
