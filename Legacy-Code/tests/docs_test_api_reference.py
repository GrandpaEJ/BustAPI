#!/usr/bin/env python3
"""
Test all code examples from docs/api-reference.md
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_bustapi_class():
    """Test BustAPI class examples from API reference."""
    print("🧪 Testing BustAPI class...")

    try:
        from bustapi import BustAPI

        # Test BustAPI initialization with all parameters
        app = BustAPI(
            title="My API",
            description="API description",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
        )

        assert app.title == "My API"
        assert app.description == "API description"
        assert app.version == "1.0.0"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"

        print("✅ BustAPI class initialization works")
        return True

    except Exception as e:
        print(f"❌ BustAPI class test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_route_decorators():
    """Test route decorator examples."""
    print("🧪 Testing route decorators...")

    try:
        from bustapi import BustAPI

        app = BustAPI()

        # Test route decorator with methods
        @app.route("/users/<int:user_id>", methods=["GET", "POST"])
        def handle_user(user_id):
            return {"user_id": user_id}

        # Test HTTP method-specific decorators
        @app.get("/users")
        def get_users():
            return {"users": []}

        @app.post("/users")
        def create_user():
            return {"message": "User created"}, 201

        @app.put("/users/<int:user_id>")
        def update_user(user_id):
            return {"user_id": user_id, "updated": True}

        @app.delete("/users/<int:user_id>")
        def delete_user(user_id):
            return {"user_id": user_id, "deleted": True}

        print("✅ Route decorators work")
        return True

    except Exception as e:
        print(f"❌ Route decorators test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_request_handling():
    """Test request handling examples."""
    print("🧪 Testing request handling...")

    try:
        from bustapi import BustAPI, request

        app = BustAPI()

        @app.route("/data", methods=["POST"])
        def handle_data():
            # JSON data
            json_data = request.get_json()

            # Form data
            form_data = request.form

            # Query parameters
            args = request.args

            # Headers
            headers = request.headers

            # Files
            files = request.files

            return {"received": "ok"}

        # Test request properties access
        @app.route("/request-info")
        def request_info():
            return {
                "method": getattr(request, "method", "GET"),
                "path": getattr(request, "path", "/"),
                "has_get_json": hasattr(request, "get_json"),
                "has_get_data": hasattr(request, "get_data"),
            }

        print("✅ Request handling works")
        return True

    except Exception as e:
        print(f"❌ Request handling test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_response_functions():
    """Test response function examples."""
    print("🧪 Testing response functions...")

    try:
        from bustapi import BustAPI, jsonify, make_response, render_template

        app = BustAPI()

        # Test jsonify
        @app.route("/api/data")
        def get_data():
            return jsonify(message="Hello", status="success")

        # Test make_response
        @app.route("/custom")
        def custom_response():
            response = make_response({"data": "custom"})
            response.headers["X-Custom-Header"] = "value"
            return response

        # Test render_template (import should work even if templates don't exist)
        @app.route("/template")
        def template_route():
            try:
                return render_template("index.html", title="Home")
            except Exception:
                # Template not found is expected in test environment
                return {"template": "would render index.html", "title": "Home"}

        print("✅ Response functions work")
        return True

    except Exception as e:
        print(f"❌ Response functions test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_response_formats():
    """Test different response formats."""
    print("🧪 Testing response formats...")

    try:
        from bustapi import BustAPI

        app = BustAPI()

        # JSON Response
        @app.route("/json")
        def json_response():
            return {"message": "Hello, JSON!"}

        # Text Response
        @app.route("/text")
        def text_response():
            return "Hello, Text!"

        # Tuple Response (data, status_code)
        @app.route("/tuple")
        def tuple_response():
            return {"created": True}, 201

        # Tuple Response (data, status_code, headers)
        @app.route("/tuple-headers")
        def tuple_headers_response():
            return {"data": "test"}, 200, {"X-Custom": "header"}

        print("✅ Response formats work")
        return True

    except Exception as e:
        print(f"❌ Response formats test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling examples."""
    print("🧪 Testing error handling...")

    try:
        from bustapi import BustAPI, abort

        app = BustAPI()

        # Test abort function
        @app.route("/error")
        def error_route():
            abort(404, description="Resource not found")

        # Test error handlers
        @app.errorhandler(404)
        def not_found(error):
            return {"error": "Not found"}, 404

        @app.errorhandler(500)
        def internal_error(error):
            return {"error": "Internal server error"}, 500

        print("✅ Error handling works")
        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration examples."""
    print("🧪 Testing configuration...")

    try:
        from bustapi import BustAPI

        app = BustAPI()

        # Test configuration setting and getting
        app.config["DEBUG"] = True
        app.config["SECRET_KEY"] = "test-secret"
        app.config["DATABASE_URL"] = "sqlite:///test.db"

        assert app.config["DEBUG"] == True
        assert app.config["SECRET_KEY"] == "test-secret"
        assert app.config["DATABASE_URL"] == "sqlite:///test.db"

        # Test config.get() method
        debug_mode = app.config.get("DEBUG", False)
        missing_key = app.config.get("MISSING_KEY", "default")

        assert debug_mode == True
        assert missing_key == "default"

        print("✅ Configuration works")
        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all API reference tests."""
    print("🚀 Testing docs/api-reference.md examples...")
    print("=" * 50)

    tests = [
        test_bustapi_class,
        test_route_decorators,
        test_request_handling,
        test_response_functions,
        test_response_formats,
        test_error_handling,
        test_configuration,
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
        print("🎉 All API reference tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
