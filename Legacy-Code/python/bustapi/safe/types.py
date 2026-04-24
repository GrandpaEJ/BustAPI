"""
Minimal runtime type safety and validation module.
Inspired by Pydantic but focused on zero-dependency simplicity.
"""

from typing import Any, Dict, Type, get_type_hints
from typing import List as TypingList


class Validator:
    """Base validator class."""

    def __init__(self, *args, **kwargs):
        pass

    def validate(self, value: Any, field_name: str) -> Any:
        raise NotImplementedError


class String(Validator):
    def validate(self, value: Any, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"Field '{field_name}' must be a string, got {type(value).__name__}"
            )
        return value


class Integer(Validator):
    def validate(self, value: Any, field_name: str) -> int:
        if not isinstance(value, int):
            raise TypeError(
                f"Field '{field_name}' must be an integer, got {type(value).__name__}"
            )
        return value


class Float(Validator):
    def validate(self, value: Any, field_name: str) -> float:
        if isinstance(value, int):
            return float(value)
        if not isinstance(value, float):
            raise TypeError(
                f"Field '{field_name}' must be a float, got {type(value).__name__}"
            )
        return value


class Boolean(Validator):
    def validate(self, value: Any, field_name: str) -> bool:
        if not isinstance(value, bool):
            raise TypeError(
                f"Field '{field_name}' must be a boolean, got {type(value).__name__}"
            )
        return value


class Const:
    """Validates that a value matches a constant."""

    def __init__(self, const_value: Any):
        self.const_value = const_value

    def validate(self, value: Any, field_name: str) -> Any:
        if value != self.const_value:
            raise ValueError(
                f"Field '{field_name}' must be '{self.const_value}', got '{value}'"
            )
        return value


class Array(Validator):
    """
    Validates a list of items.
    Usage: tags: Array(String)
    """

    def __init__(self, item_type: Any):
        self.item_type = item_type

    def validate(self, value: Any, field_name: str) -> list:
        if not isinstance(value, list):
            raise TypeError(
                f"Field '{field_name}' must be a list, got {type(value).__name__}"
            )

        result = []
        for i, item in enumerate(value):
            # Recurse validation for each item
            result.append(_validate_field(item, self.item_type, f"{field_name}[{i}]"))
        return result


def _validate_field(value: Any, type_hint: Any, field_name: str) -> Any:
    """Shared validation logic."""

    # 1. Validator Subclass (stateless)
    if (
        isinstance(type_hint, type)
        and issubclass(type_hint, Validator)
        and type_hint is not Array
    ):
        # Avoid infinite recursion if Array is passed as type
        validator = type_hint()
        return validator.validate(value, field_name)

    # 2. Struct (Nested)
    elif isinstance(type_hint, type) and issubclass(type_hint, Struct):
        if isinstance(value, dict):
            return type_hint(**value)
        elif isinstance(value, type_hint):
            return value
        else:
            raise TypeError(
                f"Field '{field_name}' must be dict or {type_hint.__name__}, got {type(value).__name__}"
            )

    # 3. Const Instance
    elif isinstance(type_hint, Const):
        return type_hint.validate(value, field_name)

    # 4. Array Instance (field: Array(String))
    elif isinstance(type_hint, Array):
        return type_hint.validate(value, field_name)

    # 5. Duck Typing (Custom validators)
    elif hasattr(type_hint, "validate"):
        return type_hint.validate(value, field_name)

    # 6. Fallback (Native types)
    else:
        if not isinstance(value, type_hint) and type_hint is not Any:
            raise TypeError(
                f"Field '{field_name}' expected {type_hint.__name__}, got {type(value).__name__}"
            )
        return value


class Struct:
    """
    Base class for type-safe data structures.
    Validates fields based on annotations during initialization.
    """

    def __init__(self, **kwargs):
        # self.__annotations__ stores the type hints defined in the class
        hints = get_type_hints(self.__class__)

        for name, type_hint in hints.items():
            if name.startswith("_"):
                continue

            value = kwargs.get(name)

            # Check for missing required fields
            if value is None:
                raise ValueError(f"Missing required field: '{name}'")

            # Validate
            validated_value = _validate_field(value, type_hint, name)
            setattr(self, name, validated_value)

    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"
