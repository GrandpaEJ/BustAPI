import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from itsdangerous import BadSignature, URLSafeTimedSerializer

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
    """Default session interface using secure cookies."""

    session_class = SecureCookieSession
    salt = "cookie-session"
    digest_method = "sha1"
    key_derivation = "hmac"
    serializer = URLSafeTimedSerializer
    session_cookie_name = "session"

    def get_signing_serializer(self, app):
        if not app.secret_key:
            return None
        return self.serializer(
            app.secret_key,
            salt=self.salt,
            serializer=json,
            # signer_kwargs={
            #     "key_derivation": self.key_derivation,
            #     "digest_method": self.digest_method,
            # },
        )

    def open_session(self, app, request: Request) -> Optional[SessionMixin]:
        s = self.get_signing_serializer(app)
        if s is None:
            return None

        val = request.cookies.get(self.session_cookie_name)
        if not val:
            return self.session_class()

        try:
            # max_age could be configured
            data = s.loads(val)  # max_age=...
            return self.session_class(data)
        except BadSignature:
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

        signer = self.get_signing_serializer(app)
        if signer is None:
            return

        if session.modified:
            val = signer.dumps(session)
            response.set_cookie(
                self.session_cookie_name,
                val,
                httponly=True,
                domain=domain,
                path=path,
                secure=app.config.get("SESSION_COOKIE_SECURE", False),
                samesite=app.config.get("SESSION_COOKIE_SAMESITE", "Lax"),
            )
