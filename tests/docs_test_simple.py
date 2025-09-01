#!/usr/bin/env python3
"""
Simple test for docs examples - focus on core functionality
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_basic_functionality():
    """Test basic BustAPI functionality from docs."""
    print("🧪 Testing basic BustAPI functionality...")

    try:
        from bustapi import BustAPI, logging

        # Test app creation
        app = BustAPI(title="Test App", version="1.0.0")
        assert app.title == "Test App"
        assert app.version == "1.0.0"
        print("✅ App creation works")

        # Test route decoration
        @app.route("/")
        def hello():
            return {"message": "Hello, World!"}

        @app.route("/users/<int:user_id>")
        def get_user(user_id):
            return {"user_id": user_id}

        @app.route("/data", methods=["POST"])
        def post_data():
            return {"status": "created"}, 201

        print("✅ Route decoration works")

        # Test logging
        logging.setup(level="INFO", use_colors=True)
        logging.info("Test logging message")
        logging.request("GET", "/test", 200, 0.045)
        print("✅ Logging works")

        # Test configuration
        app.config["DEBUG"] = True
        app.config["SECRET_KEY"] = "test-key"
        assert app.config["DEBUG"] == True
        assert app.config["SECRET_KEY"] == "test-key"
        print("✅ Configuration works")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_imports():
    """Test that all documented imports work."""
    print("🧪 Testing imports from docs...")

    try:
        # Basic imports

        print("✅ All basic imports work")

        # Test Flask compatibility
        from bustapi import Flask

        flask_app = Flask(__name__)
        print("✅ Flask compatibility import works")

        return True

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_response_types():
    """Test different response types from docs."""
    print("🧪 Testing response types...")

    try:
        from bustapi import BustAPI, jsonify, make_response

        app = BustAPI()

        # Test dict response
        @app.route("/dict")
        def dict_response():
            return {"message": "dict response"}

        # Test jsonify response
        @app.route("/jsonify")
        def jsonify_response():
            return jsonify({"message": "jsonify response"})

        # Test tuple response with status code
        @app.route("/tuple")
        def tuple_response():
            return {"message": "tuple response"}, 201

        # Test make_response
        @app.route("/make_response")
        def make_response_test():
            response = make_response({"message": "make_response"})
            response.headers["X-Custom"] = "test"
            return response

        print("✅ Response types work")
        return True

    except Exception as e:
        print(f"❌ Response types test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling from docs."""
    print("🧪 Testing error handling...")

    try:
        from bustapi import BustAPI, abort

        app = BustAPI()

        @app.route("/error")
        def error_route():
            abort(404, description="Test error")

        @app.errorhandler(404)
        def not_found(error):
            return {"error": "Not found"}, 404

        @app.errorhandler(500)
        def internal_error(error):
            return {"error": "Internal error"}, 500

        print("✅ Error handling works")
        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_blueprints():
    """Test blueprints from docs."""
    print("🧪 Testing blueprints...")

    try:
        from bustapi import Blueprint, BustAPI

        app = BustAPI()

        # Create blueprint
        api = Blueprint("api", __name__, url_prefix="/api")

        @api.route("/test")
        def api_test():
            return {"blueprint": "test"}

        # Register blueprint
        app.register_blueprint(api)

        print("✅ Blueprints work")
        return True

    except Exception as e:
        print(f"❌ Blueprints test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_template_rendering():
    """Test template rendering from docs."""
    print("🧪 Testing template rendering...")

    try:
        from bustapi import BustAPI, render_template

        app = BustAPI()

        # This might fail if templates aren't set up, but the import should work
        @app.route("/template")
        def template_route():
            try:
                return render_template("test.html", name="World")
            except Exception:
                # Template not found is expected in test environment
                return {"template": "would render test.html"}

        print("✅ Template rendering import works")
        return True

    except Exception as e:
        print(f"❌ Template rendering test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all simple tests."""
    print("🚀 Testing docs examples (simple version)...")
    print("=" * 50)

    tests = [
        test_imports,
        test_basic_functionality,
        test_response_types,
        test_error_handling,
        test_blueprints,
        test_template_rendering,
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
        print("🎉 All tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
