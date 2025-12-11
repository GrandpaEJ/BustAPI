#!/usr/bin/env python3
"""
Test all code examples from docs/quickstart.md
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_basic_app():
    """Test the basic Hello World app."""
    print("🧪 Testing basic Hello World app...")

    from bustapi import BustAPI
    from bustapi.testing import TestClient

    app = BustAPI()

    @app.route("/")
    def hello_world():
        return {"message": "Hello, World!"}

    # Test with test client
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json
    assert data["message"] == "Hello, World!"
    print("✅ Basic app test passed")


def test_routing():
    """Test basic routing examples."""
    print("🧪 Testing basic routing...")

    from bustapi import BustAPI
    from bustapi.testing import TestClient

    app = BustAPI()

    @app.route("/")
    def home():
        return {"page": "home"}

    @app.route("/about")
    def about():
        return {"page": "about"}

    @app.route("/contact")
    def contact():
        return {"page": "contact"}

    client = TestClient(app)

    # Test all routes
    response = client.get("/")
    assert response.json["page"] == "home"

    response = client.get("/about")
    assert response.json["page"] == "about"

    response = client.get("/contact")
    assert response.json["page"] == "contact"

    print("✅ Basic routing test passed")


def test_http_methods():
    """Test HTTP methods examples."""
    print("🧪 Testing HTTP methods...")

    from bustapi import BustAPI

    app = BustAPI()

    @app.route("/users", methods=["GET"])
    def get_users():
        return {"users": []}

    @app.route("/users", methods=["POST"])
    def create_user():
        return {"message": "User created"}, 201

    @app.route("/users/<int:user_id>", methods=["PUT"])
    def update_user(user_id):
        return {"message": f"User {user_id} updated"}

    @app.route("/users/<int:user_id>", methods=["DELETE"])
    def delete_user(user_id):
        return {"message": f"User {user_id} deleted"}

    client = app.test_client()

    # Test GET
    response = client.get("/users")
    assert response.status_code == 200
    assert response.get_json()["users"] == []

    # Test POST
    response = client.post("/users")
    assert response.status_code == 201
    assert "User created" in response.get_json()["message"]

    # Test PUT
    response = client.put("/users/123")
    assert response.status_code == 200
    assert "User 123 updated" in response.get_json()["message"]

    # Test DELETE
    response = client.delete("/users/123")
    assert response.status_code == 200
    assert "User 123 deleted" in response.get_json()["message"]

    print("✅ HTTP methods test passed")


def test_url_parameters():
    """Test URL parameters examples."""
    print("🧪 Testing URL parameters...")

    from bustapi import BustAPI

    app = BustAPI()

    # String parameter
    @app.route("/users/<username>")
    def show_user(username):
        return {"username": username}

    # Integer parameter
    @app.route("/posts/<int:post_id>")
    def show_post(post_id):
        return {"post_id": post_id}

    # Float parameter
    @app.route("/price/<float:price>")
    def show_price(price):
        return {"price": price}

    # Path parameter (accepts slashes)
    @app.route("/files/<path:filename>")
    def show_file(filename):
        return {"filename": filename}

    client = app.test_client()

    # Test string parameter
    response = client.get("/users/john")
    assert response.get_json()["username"] == "john"

    # Test integer parameter
    response = client.get("/posts/123")
    assert response.get_json()["post_id"] == 123

    # Test float parameter
    response = client.get("/price/19.99")
    assert response.get_json()["price"] == 19.99

    # Test path parameter
    response = client.get("/files/docs/readme.txt")
    assert response.get_json()["filename"] == "docs/readme.txt"

    print("✅ URL parameters test passed")


def test_request_handling():
    """Test request handling examples."""
    print("🧪 Testing request handling...")

    from bustapi import BustAPI, request

    app = BustAPI()

    @app.route("/data", methods=["POST"])
    def handle_data():
        # Get JSON data
        json_data = request.get_json()

        # Get form data
        form_data = request.form

        # Get query parameters
        args = request.args

        # Get headers
        headers = request.headers

        return {
            "json": json_data,
            "form": dict(form_data) if form_data else {},
            "args": dict(args) if args else {},
            "headers": dict(headers) if headers else {},
        }

    client = app.test_client()

    # Test JSON data
    response = client.post(
        "/data",
        json={"test": "data"},
        query_string={"param": "value"},
        headers={"X-Test": "header"},
    )

    data = response.get_json()
    assert data["json"]["test"] == "data"
    assert "param" in str(data["args"])

    print("✅ Request handling test passed")


def test_json_responses():
    """Test JSON response examples."""
    print("🧪 Testing JSON responses...")

    from bustapi import BustAPI, jsonify

    app = BustAPI()

    @app.route("/json")
    def json_response():
        return jsonify(
            {"message": "Hello, JSON!", "status": "success", "data": [1, 2, 3, 4, 5]}
        )

    client = app.test_client()
    response = client.get("/json")

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Hello, JSON!"
    assert data["status"] == "success"
    assert data["data"] == [1, 2, 3, 4, 5]

    print("✅ JSON responses test passed")


def test_custom_status_codes():
    """Test custom status codes examples."""
    print("🧪 Testing custom status codes...")

    from bustapi import BustAPI

    app = BustAPI()

    @app.route("/created", methods=["POST"])
    def create_resource():
        return {"message": "Resource created"}, 201

    @app.route("/not-found")
    def not_found():
        return {"error": "Resource not found"}, 404

    client = app.test_client()

    # Test 201 status
    response = client.post("/created")
    assert response.status_code == 201
    assert response.get_json()["message"] == "Resource created"

    # Test 404 status
    response = client.get("/not-found")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Resource not found"

    print("✅ Custom status codes test passed")


def test_custom_headers():
    """Test custom headers examples."""
    print("🧪 Testing custom headers...")

    from bustapi import BustAPI, make_response

    app = BustAPI()

    @app.route("/custom-headers")
    def custom_headers():
        response = make_response({"message": "Custom headers"})
        response.headers["X-Custom-Header"] = "BustAPI"
        response.headers["X-API-Version"] = "1.0"
        return response

    client = app.test_client()
    response = client.get("/custom-headers")

    assert response.status_code == 200
    assert response.headers.get("X-Custom-Header") == "BustAPI"
    assert response.headers.get("X-API-Version") == "1.0"
    assert response.get_json()["message"] == "Custom headers"

    print("✅ Custom headers test passed")


def test_error_handling():
    """Test error handling examples."""
    print("🧪 Testing error handling...")

    from bustapi import BustAPI, abort

    app = BustAPI()

    @app.route("/users/<int:user_id>")
    def get_user(user_id):
        if user_id < 1:
            abort(400, description="Invalid user ID")

        if user_id > 1000:
            abort(404, description="User not found")

        return {"user_id": user_id, "name": f"User {user_id}"}

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found", "message": str(error)}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500

    client = app.test_client()

    # Test valid user
    response = client.get("/users/123")
    assert response.status_code == 200
    data = response.get_json()
    assert data["user_id"] == 123
    assert data["name"] == "User 123"

    # Test invalid user ID (< 1)
    response = client.get("/users/0")
    assert response.status_code == 400

    # Test user not found (> 1000)
    response = client.get("/users/1001")
    assert response.status_code == 404

    print("✅ Error handling test passed")


def test_configuration():
    """Test configuration examples."""
    print("🧪 Testing configuration...")

    from bustapi import BustAPI

    app = BustAPI()

    # Development configuration
    app.config["DEBUG"] = True
    app.config["SECRET_KEY"] = "your-secret-key"

    # Custom configuration
    app.config["DATABASE_URL"] = "sqlite:///app.db"
    app.config["UPLOAD_FOLDER"] = "uploads"

    @app.route("/config")
    def show_config():
        return {
            "debug": app.config.get("DEBUG"),
            "upload_folder": app.config.get("UPLOAD_FOLDER"),
        }

    client = app.test_client()
    response = client.get("/config")

    assert response.status_code == 200
    data = response.get_json()
    assert data["debug"] == True
    assert data["upload_folder"] == "uploads"

    print("✅ Configuration test passed")


def main():
    """Run all quickstart tests."""
    print("🚀 Testing docs/quickstart.md examples...")
    print("=" * 50)

    try:
        test_basic_app()
        test_routing()
        test_http_methods()
        test_url_parameters()
        test_request_handling()
        test_json_responses()
        test_custom_status_codes()
        test_custom_headers()
        test_error_handling()
        test_configuration()

        print("=" * 50)
        print("🎉 All quickstart tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
