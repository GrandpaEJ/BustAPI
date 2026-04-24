"""
Parameter validation helpers for BustAPI.

This module provides validation helpers for path, query, and body parameters,
compatible with FastAPI's parameter validation system.
"""

import re
from typing import Any, Dict, List, Optional, Pattern, Union


class ValidationError(ValueError):
    """Exception raised when parameter validation fails."""

    def __init__(self, param_name: str, message: str):
        self.param_name = param_name
        self.message = message
        super().__init__(f"Validation error for '{param_name}': {message}")


class Path:
    """
    Path parameter validator with constraints (FastAPI-compatible).

    Use as a default value in route handler function signatures to add
    validation constraints to path parameters. Fully compatible with
    FastAPI's Path() including OpenAPI schema generation.

    Example:
        @app.route("/users/<int:user_id>")
        def get_user(user_id: int = Path(ge=1, le=1000, description="User ID")):
            return {"user_id": user_id}

    Args:
        default: Default value (usually Ellipsis ... for required parameters)
        alias: Alternative name for the parameter in the API
        title: Title for documentation
        description: Description for documentation
        example: Single example value for documentation
        examples: Multiple example values for documentation (OpenAPI 3.0+)
        ge: Greater than or equal to (for numeric types)
        le: Less than or equal to (for numeric types)
        gt: Greater than (for numeric types)
        lt: Less than (for numeric types)
        min_length: Minimum length (for strings)
        max_length: Maximum length (for strings)
        regex: Regular expression pattern (for strings)
        deprecated: Mark parameter as deprecated in documentation
        include_in_schema: Include in OpenAPI schema (default: True)
    """

    def __init__(
        self,
        default: Any = ...,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        example: Optional[Any] = None,
        examples: Optional[List[Any]] = None,
        ge: Optional[Union[int, float]] = None,
        le: Optional[Union[int, float]] = None,
        gt: Optional[Union[int, float]] = None,
        lt: Optional[Union[int, float]] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[Union[str, Pattern]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
    ):
        self.default = default
        self.alias = alias
        self.title = title
        self.description = description
        self.example = example
        self.examples = examples
        self.ge = ge
        self.le = le
        self.gt = gt
        self.lt = lt
        self.min_length = min_length
        self.max_length = max_length
        self.regex = re.compile(regex) if isinstance(regex, str) else regex
        self.deprecated = deprecated
        self.include_in_schema = include_in_schema

    def validate(self, param_name: str, value: Any) -> Any:
        """
        Validate a parameter value against the constraints.

        Args:
            param_name: Name of the parameter being validated
            value: Value to validate

        Returns:
            The validated value

        Raises:
            ValidationError: If validation fails
        """
        # Numeric constraints
        if isinstance(value, (int, float)):
            if self.ge is not None and value < self.ge:
                raise ValidationError(
                    param_name,
                    f"must be greater than or equal to {self.ge}, got {value}",
                )
            if self.le is not None and value > self.le:
                raise ValidationError(
                    param_name,
                    f"must be less than or equal to {self.le}, got {value}",
                )
            if self.gt is not None and value <= self.gt:
                raise ValidationError(
                    param_name, f"must be greater than {self.gt}, got {value}"
                )
            if self.lt is not None and value >= self.lt:
                raise ValidationError(
                    param_name, f"must be less than {self.lt}, got {value}"
                )

        # String constraints
        if isinstance(value, str):
            if self.min_length is not None and len(value) < self.min_length:
                raise ValidationError(
                    param_name,
                    f"must be at least {self.min_length} characters, got {len(value)}",
                )
            if self.max_length is not None and len(value) > self.max_length:
                raise ValidationError(
                    param_name,
                    f"must be at most {self.max_length} characters, got {len(value)}",
                )
            if self.regex is not None and not self.regex.match(value):
                raise ValidationError(
                    param_name, f"must match pattern {self.regex.pattern}"
                )

        return value

    def to_json_schema(self, param_type: str = "string") -> Dict[str, Any]:
        """
        Generate JSON Schema for OpenAPI documentation.

        Args:
            param_type: The parameter type ("string", "integer", "number")

        Returns:
            JSON Schema dictionary compatible with OpenAPI 3.0
        """
        schema: Dict[str, Any] = {"type": param_type}

        # Add title and description
        if self.title:
            schema["title"] = self.title
        if self.description:
            schema["description"] = self.description

        # Add numeric constraints
        if param_type in ("integer", "number"):
            if self.ge is not None:
                schema["minimum"] = self.ge
            if self.le is not None:
                schema["maximum"] = self.le
            if self.gt is not None:
                schema["exclusiveMinimum"] = self.gt
            if self.lt is not None:
                schema["exclusiveMaximum"] = self.lt

        # Add string constraints
        if param_type == "string":
            if self.min_length is not None:
                schema["minLength"] = self.min_length
            if self.max_length is not None:
                schema["maxLength"] = self.max_length
            if self.regex is not None:
                schema["pattern"] = self.regex.pattern

        # Add examples
        if self.example is not None:
            schema["example"] = self.example
        elif self.examples:
            schema["examples"] = self.examples

        return schema

    def to_openapi_parameter(
        self, name: str, param_type: str = "string", required: bool = True
    ) -> Dict[str, Any]:
        """
        Generate OpenAPI parameter object.

        Args:
            name: Parameter name
            param_type: The parameter type ("string", "integer", "number")
            required: Whether the parameter is required

        Returns:
            OpenAPI parameter object
        """
        param: Dict[str, Any] = {
            "name": self.alias or name,
            "in": "path",
            "required": required,
            "schema": self.to_json_schema(param_type),
        }

        # Add description at parameter level if not in schema
        if self.description and "description" not in param["schema"]:
            param["description"] = self.description

        # Mark as deprecated if specified
        if self.deprecated:
            param["deprecated"] = True

        return param

    def __repr__(self) -> str:
        constraints = []
        if self.ge is not None:
            constraints.append(f"ge={self.ge}")
        if self.le is not None:
            constraints.append(f"le={self.le}")
        if self.gt is not None:
            constraints.append(f"gt={self.gt}")
        if self.lt is not None:
            constraints.append(f"lt={self.lt}")
        if self.min_length is not None:
            constraints.append(f"min_length={self.min_length}")
        if self.max_length is not None:
            constraints.append(f"max_length={self.max_length}")
        if self.regex is not None:
            constraints.append(f"regex={self.regex.pattern!r}")
        if self.deprecated:
            constraints.append("deprecated=True")

        constraints_str = ", ".join(constraints) if constraints else ""
        return f"Path({constraints_str})"


class Query:
    """
    Query parameter validator with constraints (FastAPI-compatible).

    Use as a default value in route handler function signatures to add
    validation constraints to query parameters with automatic type coercion.

    Example:
        @app.route("/search")
        def search(q: str = Query(..., min_length=1), page: int = Query(1, ge=1)):
            return {"query": q, "page": page}

    Args:
        default: Default value (Ellipsis ... for required parameters)
        alias: Alternative name for the parameter in the API
        title: Title for documentation
        description: Description for documentation
        example: Single example value for documentation
        examples: Multiple example values for documentation (OpenAPI 3.0+)
        ge: Greater than or equal to (for numeric types)
        le: Less than or equal to (for numeric types)
        gt: Greater than (for numeric types)
        lt: Less than (for numeric types)
        min_length: Minimum length (for strings)
        max_length: Maximum length (for strings)
        regex: Regular expression pattern (for strings)
        deprecated: Mark parameter as deprecated in documentation
        include_in_schema: Include in OpenAPI schema (default: True)
    """

    def __init__(
        self,
        default: Any = ...,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        example: Optional[Any] = None,
        examples: Optional[List[Any]] = None,
        ge: Optional[Union[int, float]] = None,
        le: Optional[Union[int, float]] = None,
        gt: Optional[Union[int, float]] = None,
        lt: Optional[Union[int, float]] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[Union[str, Pattern]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
    ):
        self.default = default
        self.alias = alias
        self.title = title
        self.description = description
        self.example = example
        self.examples = examples
        self.ge = ge
        self.le = le
        self.gt = gt
        self.lt = lt
        self.min_length = min_length
        self.max_length = max_length
        self.regex = re.compile(regex) if isinstance(regex, str) else regex
        self.deprecated = deprecated
        self.include_in_schema = include_in_schema

    def coerce_type(self, value: Any, target_type: type) -> Any:
        """
        Coerce query parameter value to target type.

        Args:
            value: Raw value from query string (usually string)
            target_type: Target type to coerce to

        Returns:
            Coerced value
        """
        # Already correct type
        if isinstance(value, target_type):
            return value

        # Handle string to various types
        if isinstance(value, str):
            if target_type is int:
                return int(value)
            elif target_type is float:
                return float(value)
            elif target_type is bool:
                # Handle common boolean representations
                return value.lower() in ("true", "1", "yes", "on")
            elif target_type is str:
                return value

        # Handle list types
        if target_type is list or str(target_type).startswith("typing.List"):
            if not isinstance(value, list):
                return [value]
            return value

        # Default: return as-is
        return value

    def validate(self, param_name: str, value: Any, target_type: type = str) -> Any:
        """
        Validate and coerce a query parameter value.

        Args:
            param_name: Name of the parameter being validated
            value: Value to validate
            target_type: Target type for coercion

        Returns:
            The validated and coerced value

        Raises:
            ValidationError: If validation fails
        """
        # Coerce type first
        try:
            value = self.coerce_type(value, target_type)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                param_name, f"cannot convert to {target_type.__name__}: {str(e)}"
            ) from None

        # Numeric constraints
        if isinstance(value, (int, float)):
            if self.ge is not None and value < self.ge:
                raise ValidationError(
                    param_name,
                    f"must be greater than or equal to {self.ge}, got {value}",
                )
            if self.le is not None and value > self.le:
                raise ValidationError(
                    param_name,
                    f"must be less than or equal to {self.le}, got {value}",
                )
            if self.gt is not None and value <= self.gt:
                raise ValidationError(
                    param_name, f"must be greater than {self.gt}, got {value}"
                )
            if self.lt is not None and value >= self.lt:
                raise ValidationError(
                    param_name, f"must be less than {self.lt}, got {value}"
                )

        # String constraints
        if isinstance(value, str):
            if self.min_length is not None and len(value) < self.min_length:
                raise ValidationError(
                    param_name,
                    f"must be at least {self.min_length} characters, got {len(value)}",
                )
            if self.max_length is not None and len(value) > self.max_length:
                raise ValidationError(
                    param_name,
                    f"must be at most {self.max_length} characters, got {len(value)}",
                )
            if self.regex is not None and not self.regex.match(value):
                raise ValidationError(
                    param_name, f"must match pattern {self.regex.pattern}"
                )

        return value

    def to_json_schema(self, param_type: str = "string") -> Dict[str, Any]:
        """
        Generate JSON Schema for OpenAPI documentation.

        Args:
            param_type: The parameter type ("string", "integer", "number", "boolean")

        Returns:
            JSON Schema dictionary compatible with OpenAPI 3.0
        """
        schema: Dict[str, Any] = {"type": param_type}

        # Add title and description
        if self.title:
            schema["title"] = self.title
        if self.description:
            schema["description"] = self.description

        # Add numeric constraints
        if param_type in ("integer", "number"):
            if self.ge is not None:
                schema["minimum"] = self.ge
            if self.le is not None:
                schema["maximum"] = self.le
            if self.gt is not None:
                schema["exclusiveMinimum"] = self.gt
            if self.lt is not None:
                schema["exclusiveMaximum"] = self.lt

        # Add string constraints
        if param_type == "string":
            if self.min_length is not None:
                schema["minLength"] = self.min_length
            if self.max_length is not None:
                schema["maxLength"] = self.max_length
            if self.regex is not None:
                schema["pattern"] = self.regex.pattern

        # Add examples
        if self.example is not None:
            schema["example"] = self.example
        elif self.examples:
            schema["examples"] = self.examples

        # Add default value
        if self.default is not ... and self.default is not None:
            schema["default"] = self.default

        return schema

    def to_openapi_parameter(
        self, name: str, param_type: str = "string", required: bool = True
    ) -> Dict[str, Any]:
        """
        Generate OpenAPI parameter object.

        Args:
            name: Parameter name
            param_type: The parameter type ("string", "integer", "number", "boolean")
            required: Whether the parameter is required

        Returns:
            OpenAPI parameter object
        """
        param: Dict[str, Any] = {
            "name": self.alias or name,
            "in": "query",
            "required": required,
            "schema": self.to_json_schema(param_type),
        }

        # Add description at parameter level if not in schema
        if self.description and "description" not in param["schema"]:
            param["description"] = self.description

        # Mark as deprecated if specified
        if self.deprecated:
            param["deprecated"] = True

        return param

    def __repr__(self) -> str:
        constraints = []
        if self.default is not ...:
            constraints.append(f"default={self.default!r}")
        if self.ge is not None:
            constraints.append(f"ge={self.ge}")
        if self.le is not None:
            constraints.append(f"le={self.le}")
        if self.gt is not None:
            constraints.append(f"gt={self.gt}")
        if self.lt is not None:
            constraints.append(f"lt={self.lt}")
        if self.min_length is not None:
            constraints.append(f"min_length={self.min_length}")
        if self.max_length is not None:
            constraints.append(f"max_length={self.max_length}")
        if self.regex is not None:
            constraints.append(f"regex={self.regex.pattern!r}")
        if self.deprecated:
            constraints.append("deprecated=True")

        constraints_str = ", ".join(constraints) if constraints else ""
        return f"Query({constraints_str})"


class Body:
    """
    Request body validator with constraints (FastAPI-compatible).

    Supports both dict-based schema validation and Pydantic models.
    Use as a type annotation in route handler function signatures.

    Example (dict-based):
        @app.route("/users", methods=["POST"])
        def create_user(
            user: dict = Body(..., schema={
                "name": {"type": "str", "min_length": 1},
                "age": {"type": "int", "ge": 0}
            })
        ):
            return {"created": user}

    Example (Pydantic):
        from pydantic import BaseModel

        class User(BaseModel):
            name: str
            age: int

        @app.route("/users", methods=["POST"])
        def create_user(user: User = Body(...)):
            return {"created": user.dict()}

    Args:
        default: Default value (Ellipsis ... for required body)
        embed: Embed the body in a field with this name
        media_type: Media type (default: "application/json")
        schema: Dict-based validation schema (if not using Pydantic)
        title: Title for documentation
        description: Description for documentation
        example: Single example value for documentation
        examples: Multiple example values for documentation
    """

    def __init__(
        self,
        default: Any = ...,
        *,
        embed: Optional[str] = None,
        media_type: str = "application/json",
        schema: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        example: Optional[Any] = None,
        examples: Optional[List[Any]] = None,
    ):
        self.default = default
        self.embed = embed
        self.media_type = media_type
        self.schema = schema
        self.title = title
        self.description = description
        self.example = example
        self.examples = examples

    def validate_field(
        self, field_name: str, value: Any, field_schema: Dict[str, Any]
    ) -> Any:
        """
        Validate a single field against its schema.

        Args:
            field_name: Name of the field
            value: Value to validate
            field_schema: Schema definition for the field

        Returns:
            Validated value

        Raises:
            ValidationError: If validation fails
        """
        field_type = field_schema.get("type", "any")

        # Type coercion
        if field_type == "str" and not isinstance(value, str):
            value = str(value)
        elif field_type == "int":
            if not isinstance(value, int):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    raise ValidationError(
                        field_name, f"must be an integer, got {type(value).__name__}"
                    ) from None
        elif field_type == "float":
            if not isinstance(value, (int, float)):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    raise ValidationError(
                        field_name, f"must be a number, got {type(value).__name__}"
                    ) from None
        elif field_type == "bool":
            if not isinstance(value, bool):
                if isinstance(value, str):
                    value = value.lower() in ("true", "1", "yes", "on")
                else:
                    value = bool(value)

        # Numeric constraints
        if isinstance(value, (int, float)):
            if "ge" in field_schema and value < field_schema["ge"]:
                raise ValidationError(
                    field_name, f"must be >= {field_schema['ge']}, got {value}"
                )
            if "le" in field_schema and value > field_schema["le"]:
                raise ValidationError(
                    field_name, f"must be <= {field_schema['le']}, got {value}"
                )
            if "gt" in field_schema and value <= field_schema["gt"]:
                raise ValidationError(
                    field_name, f"must be > {field_schema['gt']}, got {value}"
                )
            if "lt" in field_schema and value >= field_schema["lt"]:
                raise ValidationError(
                    field_name, f"must be < {field_schema['lt']}, got {value}"
                )

        # String constraints
        if isinstance(value, str):
            if "min_length" in field_schema and len(value) < field_schema["min_length"]:
                raise ValidationError(
                    field_name,
                    f"must be at least {field_schema['min_length']} characters, got {len(value)}",
                )
            if "max_length" in field_schema and len(value) > field_schema["max_length"]:
                raise ValidationError(
                    field_name,
                    f"must be at most {field_schema['max_length']} characters, got {len(value)}",
                )
            if "regex" in field_schema:
                pattern = field_schema["regex"]
                if isinstance(pattern, str):
                    pattern = re.compile(pattern)
                if not pattern.match(value):
                    raise ValidationError(
                        field_name, f"must match pattern {pattern.pattern}"
                    )

        return value

    def validate(self, body_data: Any, target_type: type = dict) -> Any:
        """
        Validate request body data.

        Args:
            body_data: Parsed JSON body data
            target_type: Target type (dict or Pydantic model)

        Returns:
            Validated body data

        Raises:
            ValidationError: If validation fails
        """
        # Check if target_type is a Pydantic model
        try:
            from pydantic import BaseModel

            if isinstance(target_type, type) and issubclass(target_type, BaseModel):
                # Use Pydantic validation
                try:
                    return (
                        target_type(**body_data)
                        if isinstance(body_data, dict)
                        else target_type(body_data)
                    )
                except Exception as e:
                    raise ValidationError(
                        "body", f"Pydantic validation failed: {str(e)}"
                    ) from None
        except ImportError:
            pass

        # Dict-based validation
        if self.schema and isinstance(body_data, dict):
            validated = {}
            for field_name, field_schema in self.schema.items():
                if field_name not in body_data:
                    if field_schema.get("required", True):
                        raise ValidationError(field_name, "field is required")
                    continue

                validated[field_name] = self.validate_field(
                    field_name, body_data[field_name], field_schema
                )

            # Check for extra fields if strict mode
            if self.schema.get("__strict__", False):
                extra_fields = set(body_data.keys()) - set(self.schema.keys())
                if extra_fields:
                    raise ValidationError(
                        "body", f"unexpected fields: {', '.join(extra_fields)}"
                    )

            return validated

        return body_data

    def to_json_schema(self) -> Dict[str, Any]:
        """
        Generate JSON Schema for OpenAPI documentation.

        Returns:
            JSON Schema dictionary compatible with OpenAPI 3.0
        """
        if self.schema:
            # Convert dict schema to JSON Schema
            properties = {}
            required = []

            for field_name, field_schema in self.schema.items():
                if field_name.startswith("__"):
                    continue

                field_type = field_schema.get("type", "string")
                prop = {"type": field_type}

                if "description" in field_schema:
                    prop["description"] = field_schema["description"]
                if "example" in field_schema:
                    prop["example"] = field_schema["example"]

                # Add constraints
                if field_type in ("integer", "number"):
                    if "ge" in field_schema:
                        prop["minimum"] = field_schema["ge"]
                    if "le" in field_schema:
                        prop["maximum"] = field_schema["le"]
                    if "gt" in field_schema:
                        prop["exclusiveMinimum"] = field_schema["gt"]
                    if "lt" in field_schema:
                        prop["exclusiveMaximum"] = field_schema["lt"]

                if field_type == "string":
                    if "min_length" in field_schema:
                        prop["minLength"] = field_schema["min_length"]
                    if "max_length" in field_schema:
                        prop["maxLength"] = field_schema["max_length"]
                    if "regex" in field_schema:
                        pattern = field_schema["regex"]
                        prop["pattern"] = (
                            pattern.pattern if hasattr(pattern, "pattern") else pattern
                        )

                properties[field_name] = prop

                if field_schema.get("required", True):
                    required.append(field_name)

            schema = {"type": "object", "properties": properties}

            if required:
                schema["required"] = required

            if self.title:
                schema["title"] = self.title
            if self.description:
                schema["description"] = self.description

            return schema

        # Generic object schema
        return {"type": "object"}

    def __repr__(self) -> str:
        parts = []
        if self.default is not ...:
            parts.append(f"default={self.default!r}")
        if self.embed:
            parts.append(f"embed={self.embed!r}")
        if self.schema:
            parts.append(f"schema=<{len(self.schema)} fields>")

        parts_str = ", ".join(parts) if parts else ""
        return f"Body({parts_str})"


__all__ = ["Path", "Query", "Body", "ValidationError"]
