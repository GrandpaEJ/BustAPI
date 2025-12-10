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
    
    def to_openapi_parameter(self, name: str, param_type: str = "string", required: bool = True) -> Dict[str, Any]:
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
            "schema": self.to_json_schema(param_type)
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
            if target_type == int:
                return int(value)
            elif target_type == float:
                return float(value)
            elif target_type == bool:
                # Handle common boolean representations
                return value.lower() in ('true', '1', 'yes', 'on')
            elif target_type == str:
                return value
        
        # Handle list types
        if target_type == list or str(target_type).startswith('typing.List'):
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
                param_name,
                f"cannot convert to {target_type.__name__}: {str(e)}"
            )

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
    
    def to_openapi_parameter(self, name: str, param_type: str = "string", required: bool = True) -> Dict[str, Any]:
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
            "schema": self.to_json_schema(param_type)
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
    Request body validator with constraints.

    Similar to Path but for request body. To be implemented in Phase 2.
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Body validation is not yet implemented")


__all__ = ["Path", "Query", "Body", "ValidationError"]
