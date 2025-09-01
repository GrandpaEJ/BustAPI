"""Simple Jinja2-based templating helpers for BustAPI.

This module provides a small wrapper around Jinja2 Environment creation and
rendering so the application can call `render_template` similarly to Flask.
"""

from typing import Any, Dict, Optional

try:
    import jinja2
except Exception:  # pragma: no cover - optional dependency
    jinja2 = None


def create_jinja_env(template_folder: Optional[str] = None):
    if jinja2 is None:
        raise RuntimeError(
            "Jinja2 is not installed. Add 'jinja2' to your dependencies."
        )
    loader = jinja2.FileSystemLoader(template_folder or "templates")
    env = jinja2.Environment(loader=loader, autoescape=True)
    return env


def render_template(
    env, template_name: str, context: Optional[Dict[str, Any]] = None
) -> str:
    context = context or {}
    template = env.get_template(template_name)
    return template.render(**context)
