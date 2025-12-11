# ruff: noqa: B008
"""
Example demonstrating Body validation and Dependency Injection in BustAPI.

This example shows both dict-based body validation and the Depends() system.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from bustapi import Body, BustAPI, Depends, Query
from bustapi.documentation import BustAPIDocs

app = BustAPI()

# Initialize documentation
docs = BustAPIDocs(
    app,
    title="BustAPI Body & DI Demo",
    version="1.0.0",
    description="Demonstration of Body validation and Dependency Injection",
)


# ============================================================================
# PART 1: Body Validation Examples
# ============================================================================


@app.route("/users", methods=["POST"])
def create_user(
    user: dict = Body(
        ...,
        schema={
            "name": {
                "type": "str",
                "min_length": 1,
                "max_length": 100,
                "description": "User's full name",
            },
            "email": {
                "type": "str",
                "regex": r"^[\w\.-]+@[\w\.-]+\.\w+$",
                "description": "Email address",
            },
            "age": {"type": "int", "ge": 0, "le": 150, "description": "User's age"},
        },
    ),
):
    """
    Create a new user with validation.

    Demonstrates dict-based body validation with constraints.
    """
    return {"created": user, "status": "success"}


@app.route("/products", methods=["POST"])
def create_product(
    product: dict = Body(
        ...,
        schema={
            "name": {"type": "str", "min_length": 1, "max_length": 200},
            "price": {
                "type": "float",
                "gt": 0,
                "description": "Product price (must be positive)",
            },
            "stock": {"type": "int", "ge": 0, "description": "Stock quantity"},
            "category": {
                "type": "str",
                "regex": r"^(electronics|books|clothing|food)$",
            },
        },
    ),
):
    """
    Create a new product.

    Demonstrates numeric validation and regex patterns.
    """
    return {"product": product, "id": 12345}


@app.route("/settings", methods=["PUT"])
def update_settings(
    settings: dict = Body(
        ...,
        schema={
            "theme": {"type": "str", "regex": r"^(light|dark|auto)$"},
            "notifications": {"type": "bool"},
            "language": {"type": "str", "min_length": 2, "max_length": 5},
        },
    ),
):
    """
    Update user settings.

    Demonstrates boolean and string validation.
    """
    return {"settings": settings, "updated": True}


# ============================================================================
# PART 2: Dependency Injection Examples
# ============================================================================


# Simple dependency
def get_current_user(token: str = Query(..., description="Authentication token")):
    """Dependency that validates auth token and returns user."""
    if token == "secret":
        return {"id": 1, "name": "Alice", "role": "admin"}
    elif token == "user123":
        return {"id": 2, "name": "Bob", "role": "user"}
    from bustapi import abort

    abort(401, "Invalid authentication token")


# Database dependency with cleanup
def get_db():
    """Dependency that provides database connection with cleanup."""
    db = {"connection": "active", "queries": []}
    print("📂 Opening database connection")
    try:
        yield db
    finally:
        print("📂 Closing database connection")


# Service dependency (depends on db)
def get_user_service(db=Depends(get_db)):
    """User service that depends on database."""
    return {
        "db": db,
        "service_name": "UserService",
        "methods": ["create", "read", "update", "delete"],
    }


@app.route("/profile")
def get_profile(user=Depends(get_current_user)):
    """
    Get user profile.

    Demonstrates simple dependency injection.
    """
    return {"profile": user, "message": f"Welcome, {user['name']}!"}


@app.route("/admin/users")
def list_all_users(user=Depends(get_current_user), db=Depends(get_db)):
    """
    List all users (admin only).

    Demonstrates multiple dependencies with cleanup.
    """
    if user["role"] != "admin":
        from bustapi import abort

        abort(403, "Admin access required")

    # Simulate database query
    db["queries"].append("SELECT * FROM users")

    return {
        "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
        "admin": user["name"],
        "db_queries": db["queries"],
    }


@app.route("/admin/dashboard")
def admin_dashboard(user=Depends(get_current_user), service=Depends(get_user_service)):
    """
    Admin dashboard.

    Demonstrates nested dependencies (service depends on db).
    """
    if user["role"] != "admin":
        from bustapi import abort

        abort(403, "Admin access required")

    return {
        "admin": user,
        "service": service["service_name"],
        "available_methods": service["methods"],
        "db_status": service["db"]["connection"],
    }


# ============================================================================
# PART 3: Combined Body + Dependencies
# ============================================================================


@app.route("/admin/users/create", methods=["POST"])
def admin_create_user(
    user=Depends(get_current_user),
    db=Depends(get_db),
    new_user: dict = Body(
        ...,
        schema={
            "name": {"type": "str", "min_length": 1},
            "email": {"type": "str", "regex": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
            "role": {"type": "str", "regex": r"^(admin|user|guest)$"},
        },
    ),
):
    """
    Create user (admin only).

    Demonstrates Body validation + Dependency Injection together.
    """
    if user["role"] != "admin":
        from bustapi import abort

        abort(403, "Admin access required")

    # Simulate database insert
    db["queries"].append(f"INSERT INTO users VALUES ({new_user})")

    return {
        "created_by": user["name"],
        "new_user": new_user,
        "db_queries": db["queries"],
    }


if __name__ == "__main__":
    print("🚀 Body Validation & Dependency Injection Demo")
    print("=" * 60)
    print("\nDocumentation URLs:")
    print("  Swagger UI:  http://127.0.0.1:5023/docs")
    print("  ReDoc:       http://127.0.0.1:5023/redoc")
    print("  OpenAPI:     http://127.0.0.1:5023/openapi.json")
    print("\nExample Requests:")
    print("\n  # Body Validation")
    print("  curl -X POST http://localhost:5023/users \\")
    print("    -H 'Content-Type: application/json' \\")
    print('    -d \'{"name":"Alice","email":"alice@example.com","age":30}\'')
    print("\n  # Dependency Injection")
    print("  curl 'http://localhost:5023/profile?token=secret'")
    print("  curl 'http://localhost:5023/admin/users?token=secret'")
    print("\n  # Combined (Body + DI)")
    print("  curl -X POST 'http://localhost:5023/admin/users/create?token=secret' \\")
    print("    -H 'Content-Type: application/json' \\")
    print('    -d \'{"name":"Bob","email":"bob@example.com","role":"user"}\'')
    print("\n  # Validation Errors")
    print("  curl -X POST http://localhost:5023/users \\")
    print("    -H 'Content-Type: application/json' \\")
    print('    -d \'{"name":"","email":"invalid","age":200}\'  # Should return 400')
    print("\n" + "=" * 60)

    app.run(port=5023, workers=2, debug=True)
