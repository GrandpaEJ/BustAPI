"""
Example: JWT Authentication with Blueprints

This example demonstrates the CORRECT way to use JWT with Blueprints in BustAPI.

IMPORTANT: Initialize JWT on the main app, not in the blueprint file!

Run:
    python examples/routing/blueprint_with_jwt.py

Test with:
    # Login
    curl -X POST http://localhost:5000/auth/login \
         -H "Content-Type: application/json" \
         -d '{"username": "admin", "password": "secret123"}'

    # Access protected route
    curl http://localhost:5000/auth/protected \
         -H "Authorization: Bearer <token>"

    # Refresh token
    curl -X POST http://localhost:5000/auth/refresh \
         -H "Authorization: Bearer <refresh_token>"
"""

from bustapi import (
    JWT,
    Blueprint,
    BustAPI,
    hash_password,
    jwt_refresh_token_required,
    jwt_required,
    request,
    verify_password,
)

# ============================================================================
# BLUEPRINT DEFINITION (auth_routes.py in a real app)
# ============================================================================

# Create the blueprint
auth_bp = Blueprint(name="auth", import_name=__name__, url_prefix="/auth")

# Simulated user database
USERS = {
    "admin": hash_password("secret123"),
    "user": hash_password("password"),
}


@auth_bp.post("/login")
def login():
    """Login and get access + refresh tokens."""
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "Missing username or password"}, 400

    stored_hash = USERS.get(username)
    if not stored_hash or not verify_password(password, stored_hash):
        return {"error": "Invalid credentials"}, 401

    # Access JWT from the current app's extensions
    # This works because JWT was initialized on the main app
    jwt_ext = request.app.extensions.get("jwt")

    # Create tokens
    access_token = jwt_ext.create_access_token(identity=username, fresh=True)
    refresh_token = jwt_ext.create_refresh_token(identity=username)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@auth_bp.get("/protected")
@jwt_required
def protected():
    """Protected route - requires valid JWT."""
    return {
        "message": f"Hello, {request.jwt_identity}!",
        "claims": request.jwt_claims,
    }


@auth_bp.get("/fresh-only")
@jwt_required
def fresh_only():
    """Route that requires a fresh token (from login, not refresh)."""
    if not request.jwt_claims.get("fresh", False):
        return {"error": "Fresh token required"}, 401

    return {
        "message": "This route requires a fresh token",
        "user": request.jwt_identity,
    }


@auth_bp.post("/refresh")
@jwt_refresh_token_required
def refresh():
    """Get a new access token using refresh token."""
    jwt_ext = request.app.extensions.get("jwt")

    # Create new access token (not fresh since it's from refresh)
    new_access_token = jwt_ext.create_access_token(
        identity=request.jwt_identity,
        fresh=False,
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


# ============================================================================
# MAIN APPLICATION (main.py in a real app)
# ============================================================================

if __name__ == "__main__":
    # Create the main application
    app = BustAPI(__name__)
    app.secret_key = "your-super-secret-key-change-in-production"

    # ✅ CORRECT: Initialize JWT on the MAIN app
    jwt = JWT(app)

    # Register the blueprint
    app.register_blueprint(auth_bp)

    # Add a public route on the main app
    @app.get("/")
    def home():
        return {"message": "Welcome! Use /auth/login to get started"}

    print("Blueprint JWT Authentication Example")
    print("-" * 40)
    print("Endpoints:")
    print("  GET  /                - Public home")
    print("  POST /auth/login      - Get tokens")
    print("  GET  /auth/protected  - Requires JWT")
    print("  GET  /auth/fresh-only - Requires fresh JWT")
    print("  POST /auth/refresh    - Refresh access token")
    print("-" * 40)
    print()
    print("✅ CORRECT PATTERN:")
    print("   - JWT initialized on main app")
    print("   - Blueprint registered to main app")
    print("   - Routes access JWT via request.app.extensions['jwt']")
    print("-" * 40)

    app.run(debug=True)
