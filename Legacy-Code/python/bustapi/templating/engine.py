"""MiniJinja-based templating helpers for BustAPI.

This module provides a wrapper around MiniJinja Environment creation and
rendering, replacing the previous Jinja2 integration.
"""

from typing import Any, Dict, Optional

try:
    import minijinja
except ImportError:  # pragma: no cover - optional dependency
    minijinja = None


def create_template_env(template_folder: Optional[str] = None):
    if minijinja is None:
        raise RuntimeError(
            "MiniJinja is not installed. Add 'minijinja' to your dependencies."
        )

    env = minijinja.Environment(
        loader=lambda n: open(f"{template_folder or 'templates'}/{n}").read()
    )
    return env


def create_jinja_env(template_folder: Optional[str] = None):
    """Backwards compatibility alias for create_template_env."""
    return create_template_env(template_folder)


def render_template(
    env, template_name: str, context: Optional[Dict[str, Any]] = None
) -> str:
    context = context or {}
    return env.render_template(template_name, **context)
