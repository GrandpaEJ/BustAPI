#!/usr/bin/env python3
"""
Standalone test script for Path validation.
This can be run directly without pytest to verify functionality.
"""

import os
import sys

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from bustapi.params import Path, ValidationError


def test_numeric_constraints():
    """Test numeric validation constraints."""
    print("Testing numeric constraints...")

    # Test ge (greater than or equal)
    validator = Path(ge=1, le=100)

    # Valid values
    assert validator.validate("test_param", 1) == 1
    assert validator.validate("test_param", 50) == 50
    assert validator.validate("test_param", 100) == 100

    # Invalid: too low
    try:
        validator.validate("test_param", 0)
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        assert "greater than or equal" in str(e)
        print(f"  ✓ Correctly rejected value 0: {e.message}")

    # Invalid: too high
    try:
        validator.validate("test_param", 101)
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        assert "less than or equal" in str(e)
        print(f"  ✓ Correctly rejected value 101: {e.message}")

    print("✅ Numeric constraints test passed\n")


def test_string_length():
    """Test string length constraints."""
    print("Testing string length constraints...")

    validator = Path(min_length=3, max_length=10)

    # Valid values
    assert validator.validate("username", "abc") == "abc"
    assert validator.validate("username", "hello") == "hello"
    assert validator.validate("username", "1234567890") == "1234567890"

    # Invalid: too short
    try:
        validator.validate("username", "ab")
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        assert "at least 3 characters" in str(e)
        print(f"  ✓ Correctly rejected short string: {e.message}")

    # Invalid: too long
    try:
        validator.validate("username", "12345678901")
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        assert "at most 10 characters" in str(e)
        print(f"  ✓ Correctly rejected long string: {e.message}")

    print("✅ String length test passed\n")


def test_regex_pattern():
    """Test regex pattern matching."""
    print("Testing regex pattern matching...")

    validator = Path(regex=r"^[a-z0-9-]+$")

    # Valid values
    assert validator.validate("slug", "hello-world") == "hello-world"
    assert validator.validate("slug", "test123") == "test123"
    assert validator.validate("slug", "api-v2") == "api-v2"

    # Invalid: contains uppercase
    try:
        validator.validate("slug", "Hello")
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        assert "must match pattern" in str(e)
        print(f"  ✓ Correctly rejected uppercase: {e.message}")

    # Invalid: contains special chars
    try:
        validator.validate("slug", "hello_world")
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        assert "must match pattern" in str(e)
        print(f"  ✓ Correctly rejected underscore: {e.message}")

    print("✅ Regex pattern test passed\n")


def test_gt_lt_constraints():
    """Test strict greater-than and less-than."""
    print("Testing gt/lt constraints...")

    validator = Path(gt=0, lt=10)

    # Valid values
    assert validator.validate("value", 1) == 1
    assert validator.validate("value", 5) == 5
    assert validator.validate("value", 9) == 9

    # Invalid: equal to lower bound
    try:
        validator.validate("value", 0)
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        assert "greater than" in str(e)
        print(f"  ✓ Correctly rejected value 0: {e.message}")

    # Invalid: equal to upper bound
    try:
        validator.validate("value", 10)
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        assert "less than" in str(e)
        print(f"  ✓ Correctly rejected value 10: {e.message}")

    print("✅ gt/lt constraints test passed\n")


def test_float_validation():
    """Test float validation."""
    print("Testing float validation...")

    validator = Path(ge=0.01, le=999.99)

    # Valid values
    assert validator.validate("price", 0.01) == 0.01
    assert validator.validate("price", 19.99) == 19.99
    assert validator.validate("price", 999.99) == 999.99

    # Invalid: too low
    try:
        validator.validate("price", 0.00)
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        assert "greater than or equal" in str(e)
        print(f"  ✓ Correctly rejected value 0.00: {e.message}")

    # Invalid: too high
    try:
        validator.validate("price", 1000.00)
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        assert "less than or equal" in str(e)
        print(f"  ✓ Correctly rejected value 1000.00: {e.message}")

    print("✅ Float validation test passed\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Path Validation Unit Tests")
    print("=" * 60)
    print()

    try:
        test_numeric_constraints()
        test_string_length()
        test_regex_pattern()
        test_gt_lt_constraints()
        test_float_validation()

        print("=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
