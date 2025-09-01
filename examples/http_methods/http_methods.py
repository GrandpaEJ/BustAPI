#!/usr/bin/env python3
"""
HTTP Methods Examples

This example demonstrates all HTTP methods supported by BustAPI:
- GET: Retrieve data
- POST: Create new resources
- PUT: Update/replace resources
- PATCH: Partial updates
- DELETE: Remove resources
- HEAD: Get headers only
- OPTIONS: Get allowed methods
"""

from bustapi import BustAPI, jsonify, request

app = BustAPI()

# In-memory storage for demonstration
users = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
}
next_user_id = 3


# GET - Retrieve data
@app.route("/users", methods=["GET"])
def get_users():
    """Get all users"""
    return {"users": list(users.values()), "count": len(users), "method": "GET"}


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Get a specific user"""
    if user_id not in users:
        return {"error": "User not found"}, 404

    return {"user": users[user_id], "method": "GET"}


# POST - Create new resources
@app.route("/users", methods=["POST"])
def create_user():
    """Create a new user"""
    global next_user_id

    data = request.get_json()
    if not data or "name" not in data or "email" not in data:
        return {"error": "Name and email are required"}, 400

    new_user = {"id": next_user_id, "name": data["name"], "email": data["email"]}

    users[next_user_id] = new_user
    next_user_id += 1

    return {
        "user": new_user,
        "message": "User created successfully",
        "method": "POST",
    }, 201


# PUT - Update/replace entire resource
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """Update/replace a user"""
    if user_id not in users:
        return {"error": "User not found"}, 404

    data = request.get_json()
    if not data or "name" not in data or "email" not in data:
        return {"error": "Name and email are required"}, 400

    users[user_id] = {"id": user_id, "name": data["name"], "email": data["email"]}

    return {
        "user": users[user_id],
        "message": "User updated successfully",
        "method": "PUT",
    }


# PATCH - Partial update
@app.route("/users/<int:user_id>", methods=["PATCH"])
def patch_user(user_id):
    """Partially update a user"""
    if user_id not in users:
        return {"error": "User not found"}, 404

    data = request.get_json()
    if not data:
        return {"error": "No data provided"}, 400

    user = users[user_id]
    if "name" in data:
        user["name"] = data["name"]
    if "email" in data:
        user["email"] = data["email"]

    return {"user": user, "message": "User partially updated", "method": "PATCH"}


# DELETE - Remove resource
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete a user"""
    if user_id not in users:
        return {"error": "User not found"}, 404

    deleted_user = users.pop(user_id)

    return {
        "message": f"User {user_id} deleted successfully",
        "deleted_user": deleted_user,
        "method": "DELETE",
    }


# HEAD - Get headers only (no body)
@app.route("/users/<int:user_id>", methods=["HEAD"])
def head_user(user_id):
    """Get user headers only"""
    if user_id not in users:
        return "", 404

    # HEAD requests should return empty body but appropriate headers
    response = jsonify({})
    response.headers["X-User-Exists"] = "true"
    response.headers["X-User-ID"] = str(user_id)
    return response


# OPTIONS - Get allowed methods
@app.route("/users", methods=["OPTIONS"])
def options_users():
    """Get allowed methods for users collection"""
    response = jsonify(
        {
            "allowed_methods": ["GET", "POST", "OPTIONS"],
            "description": "Users collection endpoint",
        }
    )
    response.headers["Allow"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/users/<int:user_id>", methods=["OPTIONS"])
def options_user(user_id):
    """Get allowed methods for specific user"""
    response = jsonify(
        {
            "allowed_methods": ["GET", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
            "description": f"User {user_id} endpoint",
        }
    )
    response.headers["Allow"] = "GET, PUT, PATCH, DELETE, HEAD, OPTIONS"
    response.headers["Access-Control-Allow-Methods"] = (
        "GET, PUT, PATCH, DELETE, HEAD, OPTIONS"
    )
    return response


# Demonstration endpoint showing all methods
@app.route(
    "/demo", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
)
def demo_all_methods():
    """Demonstrate handling multiple methods in one endpoint"""
    method = request.method

    responses = {
        "GET": {"message": "This is a GET request", "data": "Retrieved data"},
        "POST": {"message": "This is a POST request", "action": "Created resource"},
        "PUT": {"message": "This is a PUT request", "action": "Updated resource"},
        "PATCH": {"message": "This is a PATCH request", "action": "Partially updated"},
        "DELETE": {"message": "This is a DELETE request", "action": "Deleted resource"},
        "HEAD": {"message": "This is a HEAD request"},
        "OPTIONS": {
            "message": "This is an OPTIONS request",
            "allowed_methods": [
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
                "HEAD",
                "OPTIONS",
            ],
        },
    }

    response_data = responses.get(method, {"message": "Unknown method"})
    response_data["method"] = method

    if method == "HEAD":
        return "", 200

    return response_data


if __name__ == "__main__":
    print("🚀 Starting HTTP Methods Examples...")
    print("\n📍 Test these endpoints:")
    print("   GET    http://127.0.0.1:8000/users")
    print("   GET    http://127.0.0.1:8000/users/1")
    print("   POST   http://127.0.0.1:8000/users")
    print("   PUT    http://127.0.0.1:8000/users/1")
    print("   PATCH  http://127.0.0.1:8000/users/1")
    print("   DELETE http://127.0.0.1:8000/users/1")
    print("   HEAD   http://127.0.0.1:8000/users/1")
    print("   OPTIONS http://127.0.0.1:8000/users")
    print("\n💡 Use curl or a tool like Postman to test different methods")

    app.run(host="127.0.0.1", port=8000, debug=True)
