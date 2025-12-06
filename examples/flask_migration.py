"""
Flask Migration Example for BustAPI

This example shows how to migrate from Flask to BustAPI with minimal changes.
"""

# Original Flask code (commented out):
# from flask import Flask, request, jsonify, Blueprint
# app = Flask(__name__)

# BustAPI equivalent - just change the import!
from bustapi import Blueprint, Flask, jsonify, request

app = Flask(__name__)

# Create a blueprint (Flask-compatible)
api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/users")
def get_users():
    """Get all users."""
    # Mock user data
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
    ]
    return jsonify({"users": users, "count": len(users)})


# NOTE: Dynamic routing is currently disabled due to a backend issue.
# @api_bp.route("/users/<int:user_id>")
# def get_user(user_id):
#     """Get a specific user by ID."""
#     # Mock user lookup
#     if user_id > 0 and user_id <= 3:
#         user = {
#             "id": user_id,
#             "name": f"User{user_id}",
#             "email": f"user{user_id}@example.com",
#         }
#         return jsonify({"user": user})
#     else:
#         return jsonify({"error": "User not found"}), 404


@api_bp.route("/users", methods=["POST"])
def create_user():
    """Create a new user."""
    data = request.json

    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400

    # Mock user creation
    new_user = {
        "id": 999,  # Mock ID
        "name": data["name"],
        "email": data.get("email", f"{data['name'].lower()}@example.com"),
    }

    return jsonify({"user": new_user, "message": "User created successfully"}), 201


# Register the blueprint
app.register_blueprint(api_bp)


# Main routes
@app.route("/")
def index():
    """Index page."""
    return jsonify(
        {
            "message": "BustAPI Flask Migration Example",
            "framework": "BustAPI (Flask-compatible)",
            "endpoints": {
                "users": "/api/users",
                "user_detail": "/api/users/<id>",
                "create_user": "POST /api/users",
            },
        }
    )


@app.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "framework": "BustAPI", "version": "0.1.0"})


# Error handlers (Flask-compatible)
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# Before/after request handlers (Flask-compatible)
@app.before_request
def before_request():
    """Log before each request."""
    print(f"🔄 {request.method} {request.path}")


@app.after_request
def after_request(response):
    """Add custom headers after each request."""
    response.headers["X-Powered-By"] = "BustAPI"
    response.headers["X-Framework"] = "Flask-Compatible"
    return response


if __name__ == "__main__":
    print("🔄 Flask → BustAPI Migration Example")
    print("📝 This code runs on both Flask and BustAPI!")
    print()
    print("🌐 Available endpoints:")
    print("   GET  /                - Index")
    print("   GET  /health          - Health check")
    print("   GET  /api/users       - List all users")
    print("   GET  /api/users/<id>  - Get specific user")
    print("   POST /api/users       - Create new user")
    print()
    print("💡 To test POST endpoint:")
    print("   curl -X POST http://localhost:5000/api/users \\")
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"name": "Dave", "email": "dave@example.com"}\'')
    print()

    try:
        app.run(host="127.0.0.1", port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Migration example stopped!")
