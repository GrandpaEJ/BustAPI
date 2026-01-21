"""
Application and Request context managers for BustAPI.
"""

from .http.request import _request_ctx


class _AppContext:
    """Application context manager (placeholder for Flask compatibility)."""

    def __init__(self, app):
        self.app = app

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class _RequestContext:
    """Request context manager for test and CLI usage."""

    def __init__(self, app, environ):
        self.app = app
        self.environ = environ
        self.token = None

    def __enter__(self):
        # Create a mock request for testing/cli
        class MockRequest:
            def __init__(self):
                self.method = "GET"
                self.path = "/"
                self.args = {}
                self.form = {}
                self.json = {}
                self.headers = {}
                self.cookies = {}
                self.session = {}
                self.remote_addr = "127.0.0.1"
                self.url = "http://localhost/"
                self.base_url = "http://localhost/"
                self.host = "localhost"
                self.scheme = "http"
                self.is_secure = False
                self.data = b""
                self.content_type = None
                self.content_length = 0

        # If environ is a real Request-like object, use it; otherwise create mock
        if self.environ and hasattr(self.environ, "method"):
            request = self.environ
        else:
            request = MockRequest()

        # Push request context
        self.token = _request_ctx.set(request)
        return request

    def __exit__(self, exc_type, exc_value, traceback):
        if self.token is not None:
            _request_ctx.reset(self.token)


class ContextMixin:
    """Mixin providing context management methods."""

    def app_context(self):
        """Create application context."""
        return _AppContext(self)

    def request_context(self, environ_or_request):
        """Create request context."""
        return _RequestContext(self, environ_or_request)

    def test_request_context(self, *args, **kwargs):
        """Create test request context."""
        return _RequestContext(self, None)

    def shell_context_processor(self, f):
        """Register a shell context processor function."""
        self.shell_context_processors.append(f)
        return f

    def make_shell_context(self):
        """Create shell context."""
        context = {"app": self}
        for processor in self.shell_context_processors:
            context.update(processor())
        return context
