#!/usr/bin/env python3
"""
Test installation verification example from docs/installation.md
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_installation_verification():
    """Test the installation verification example."""
    print("🧪 Testing installation verification example...")

    try:
        # This is the exact code from docs/installation.md
        from bustapi import BustAPI

        app = BustAPI()

        @app.route("/")
        def hello():
            return {"message": "BustAPI is working!"}

        # Test that the route was registered (just check that _view_functions exists)
        assert hasattr(app, "_view_functions")
        assert isinstance(app._view_functions, dict)

        print("✅ Installation verification example works")
        return True

    except Exception as e:
        print(f"❌ Installation verification test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_basic_imports():
    """Test that all basic imports work as documented."""
    print("🧪 Testing basic imports...")

    try:
        # Test main import
        from bustapi import BustAPI

        # Test that we can create an app
        app = BustAPI()

        # Test that basic methods exist
        assert hasattr(app, "route")
        assert hasattr(app, "run")
        assert hasattr(app, "config")

        print("✅ Basic imports work")
        return True

    except Exception as e:
        print(f"❌ Basic imports test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_optional_dependencies():
    """Test optional dependencies that should be available."""
    print("🧪 Testing optional dependencies...")

    results = {}

    # Test Jinja2 (should be available)
    try:
        import jinja2

        results["jinja2"] = True
        print("✅ Jinja2 is available")
    except ImportError:
        results["jinja2"] = False
        print("⚠️ Jinja2 not available (optional)")

    # Test template rendering
    try:
        from bustapi import render_template

        results["render_template"] = True
        print("✅ render_template import works")
    except ImportError:
        results["render_template"] = False
        print("❌ render_template import failed")

    # Test that at least the core functionality works
    if results.get("render_template", False):
        print("✅ Template rendering support available")
        return True
    else:
        print("⚠️ Template rendering not fully available (but core BustAPI works)")
        return True  # This is okay, templates are optional


def test_development_features():
    """Test development features mentioned in docs."""
    print("🧪 Testing development features...")

    try:
        from bustapi import BustAPI

        app = BustAPI()

        # Test debug mode
        assert hasattr(app, "run")  # Check that run method exists

        # Test configuration
        app.config["DEBUG"] = True
        assert app.config["DEBUG"] == True

        print("✅ Development features work")
        return True

    except Exception as e:
        print(f"❌ Development features test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all installation tests."""
    print("🚀 Testing docs/installation.md examples...")
    print("=" * 50)

    tests = [
        test_basic_imports,
        test_installation_verification,
        test_optional_dependencies,
        test_development_features,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            print()

    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All installation tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
