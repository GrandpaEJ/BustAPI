from typing import Any, Dict, Optional

from ..responses import HTMLResponse


class TemplatingMixin:
    """Mixin for templating support."""

    template_folder: Optional[str]
    jinja_options: Dict[str, Any]
    jinja_env: Any
    _rust_app: Any

    def create_jinja_environment(self):
        """Create Jinja2 environment."""
        if self.jinja_env is None:
            try:
                from jinja2 import Environment, FileSystemLoader

                template_folder = self.template_folder or "templates"
                self.jinja_env = Environment(
                    loader=FileSystemLoader(template_folder), **self.jinja_options
                )
            except ImportError:
                pass
        return self.jinja_env

    def create_jinja_env(self):
        """Create and cache a Jinja2 environment."""
        if self.jinja_env is None:
            try:
                from .engine import create_jinja_env as _create_env

                self.jinja_env = _create_env(self.template_folder)
            except Exception as e:
                raise RuntimeError(f"Failed to create Jinja environment: {e}") from e
        return self.jinja_env

    def render_template(self, template_name: str, **context) -> HTMLResponse:
        """Render a template using the native Rust engine."""
        import json

        html_content = self._rust_app.render_template(
            template_name, json.dumps(context)
        )
        return HTMLResponse(html_content)
