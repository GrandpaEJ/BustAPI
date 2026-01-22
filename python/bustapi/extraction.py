"""
Parameter extraction and dependency resolution for BustAPI routes.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import BustAPI


class ExtractionMixin:
    """Mixin providing parameter extraction and dependency resolution."""

    def _extract_path_params(self, rule: str, method: str, path: str):
        """Extract and validate path params from a Flask-style rule like '/greet/<name>' or '/users/<int:id>'."""
        if "<" not in rule:
            return [], {}

        rule_parts = rule.strip("/").split("/")
        path_parts = path.strip("/").split("/")
        args = []
        kwargs = {}
        if len(rule_parts) != len(path_parts):
            return args, kwargs

        # Get validators for this rule and method once
        validators = self.path_validators.get((rule, method), {})

        for rp, pp in zip(rule_parts, path_parts):
            if rp.startswith("<") and rp.endswith(">"):
                inner = rp[1:-1]  # strip < >
                if ":" in inner:
                    typ, name = inner.split(":", 1)
                    typ = typ.strip()
                    name = name.strip()
                else:
                    typ = "str"
                    name = inner.strip()
                val = pp
                if typ == "int":
                    try:
                        val = int(pp)
                    except ValueError:
                        val = pp
                elif typ == "float":
                    try:
                        val = float(pp)
                    except ValueError:
                        val = pp

                # Validate against Path constraints if present
                validator = validators.get(name)
                if validator:
                    from .params import ValidationError

                    try:
                        val = validator.validate(name, val)
                    except ValidationError as e:
                        from .core.helpers import abort

                        abort(400, description=str(e))

                # Only populate kwargs to avoid duplicate positional+keyword arguments
                kwargs[name] = val
        return args, kwargs

    def _validate_path_params(self, rule: str, method: str, params: dict) -> dict:
        """Validate pre-extracted path params against Path constraints.

        Used when params are extracted by Rust for performance, but still
        need Python-side validation (ge, le, regex, etc).
        """
        validators = self.path_validators.get((rule, method), {})
        if not validators:
            return params  # No validators, return as-is

        validated = {}
        for name, val in params.items():
            validator = validators.get(name)
            if validator:
                from .params import ValidationError

                try:
                    val = validator.validate(name, val)
                except ValidationError as e:
                    from .core.helpers import abort

                    abort(400, description=str(e))
            validated[name] = val

        return validated

    def _extract_query_params(self, rule: str, request):
        """Extract and validate query parameters based on Query validators."""
        # FAST PATH: If no query validators registered for this route, return empty kwargs
        validators = self.query_validators.get((rule, request.method))
        if not validators:
            return {}

        kwargs = {}

        for param_name, (query_validator, param_type) in validators.items():
            # Get raw value from query string
            raw_value = request.args.get(param_name)

            # Handle required vs optional
            if raw_value is None:
                if query_validator.default is ...:
                    # Required parameter is missing
                    from .core.helpers import abort

                    abort(
                        400,
                        description=f"Missing required query parameter: {param_name}",
                    )
                else:
                    # Use default value
                    kwargs[param_name] = query_validator.default
                    continue

            # Validate and coerce the value
            try:
                validated_value = query_validator.validate(
                    param_name, raw_value, param_type
                )
                kwargs[param_name] = validated_value
            except Exception as e:
                from .core.helpers import abort

                abort(400, description=str(e))

        return kwargs

    def _extract_body_params(self, rule: str, request):
        """Extract and validate request body based on Body validators."""
        # FAST PATH: If no body validators registered for this route, return empty kwargs
        validators = self.body_validators.get((rule, request.method))
        if not validators:
            return {}

        kwargs = {}

        for param_name, (body_validator, param_type) in validators.items():
            # Parse JSON body
            body_data = None
            try:
                if request.is_json:
                    body_data = request.get_json()
                elif request.data:
                    import json

                    body_data = json.loads(request.data.decode("utf-8"))
            except Exception:
                pass

            # Handle missing body
            if body_data is None:
                if body_validator.default is ...:
                    from .core.helpers import abort

                    abort(400, description="Missing required request body")
                else:
                    continue

            # Validate the body
            try:
                validated_value = body_validator.validate(body_data, param_type)
                kwargs[param_name] = validated_value
            except Exception as e:
                from .core.helpers import abort

                abort(400, description=str(e))

        return kwargs

    def _resolve_dependencies(self, rule: str, method: str, resolved_params: dict):
        """Resolve dependencies for this route (sync version)."""
        # FAST PATH: If no dependencies registered for this route, return empty kwargs
        deps = self.dependencies.get((rule, method))
        if not deps:
            return {}, None

        from .dependencies import DependencyCache, resolve_dependency_sync

        kwargs = {}
        cache = DependencyCache()

        for param_name, depends in deps.items():
            value = resolve_dependency_sync(depends, cache, resolved_params)
            kwargs[param_name] = value

        return kwargs, cache

    async def _resolve_dependencies_async(
        self, rule: str, method: str, resolved_params: dict
    ):
        """Resolve dependencies for this route (async version)."""
        # FAST PATH: If no dependencies registered for this route, return empty kwargs
        deps = self.dependencies.get((rule, method))
        if not deps:
            return {}, None

        from .dependencies import DependencyCache, resolve_dependency

        kwargs = {}
        cache = DependencyCache()

        for param_name, depends in deps.items():
            value = await resolve_dependency(depends, cache, resolved_params)
            kwargs[param_name] = value

        return kwargs, cache

    def _register_func_params(
        self, rule: str, method: str, func, is_top_level: bool = True
    ):
        """
        Recursively register (flatten) parameters from a function and its dependencies.

        Args:
            rule: The URL rule string
            method: The HTTP method
            func: The function to inspect
            is_top_level: Whether this is the main view function (register dependencies)
                          or a nested dependency (only register params)
        """
        import inspect

        from .dependencies import Depends
        from .params import Body, Path, Query

        try:
            sig = inspect.signature(func)
        except (ValueError, TypeError):
            return

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            default = param.default
            annotation = (
                param.annotation
                if param.annotation is not inspect.Parameter.empty
                else None
            )

            if isinstance(default, Query):
                if (rule, method) not in self.query_validators:
                    self.query_validators[(rule, method)] = {}
                self.query_validators[(rule, method)][param_name] = (
                    default,
                    annotation,
                )

            elif isinstance(default, Body):
                if (rule, method) not in self.body_validators:
                    self.body_validators[(rule, method)] = {}
                self.body_validators[(rule, method)][param_name] = (default, annotation)

            elif isinstance(default, Path):
                if (rule, method) not in self.path_validators:
                    self.path_validators[(rule, method)] = {}
                self.path_validators[(rule, method)][param_name] = default

            elif isinstance(default, Depends):
                # Only register dependency at top-level
                if is_top_level:
                    if (rule, method) not in self.dependencies:
                        self.dependencies[(rule, method)] = {}
                    self.dependencies[(rule, method)][param_name] = default

                # Recurse into dependency function to register its params
                if default.dependency:
                    self._register_func_params(
                        rule, method, default.dependency, is_top_level=False
                    )
