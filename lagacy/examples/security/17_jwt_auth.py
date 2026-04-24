"""
Example: JWT Authentication with BustAPI

This example demonstrates how to use the JWT extension for
token-based authentication with Rust-backed JWT encoding/decoding.

Run:
    python examples/17_jwt_auth.py

Test with:
    # Login
    curl -X POST http://localhost:5000/login -H "Content-Type: application/json" \
         -d '{"username": "admin", "password": "secret123"}'

    # Access protected route (use token from login response)
    curl http://localhost:5000/protected -H "Authorization: Bearer <token>"

    # Access fresh-only route
    curl http://localhost:5000/fresh-only -H "Authorization: Bearer <token>"

    # Refresh token
    curl -X POST http://localhost:5000/refresh -H "Authorization: Bearer <refresh_token>"
"""

from bustapi import (
    JWT,
    BustAPI,
    fresh_jwt_required,
    hash_password,
    jwt_refresh_token_required,
    jwt_required,
    verify_password,
)

app = BustAPI(__name__)
app.secret_key = "your-super-secret-key-change-in-production"

# Initialize JWT
jwt = JWT(app)

# Simulated user database
USERS = {
    "admin": hash_password("secret123"),
    "user": hash_password("password"),
}


@app.post("/login")
def login(request):
    """Login and get access + refresh tokens."""
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "Missing username or password"}, 400

    stored_hash = USERS.get(username)
    if not stored_hash or not verify_password(password, stored_hash):
        return {"error": "Invalid credentials"}, 401

    # Create tokens
    access_token = jwt.create_access_token(identity=username, fresh=True)
    refresh_token = jwt.create_refresh_token(identity=username)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.get("/protected")
@jwt_required
def protected(request):
    """Protected route - requires valid JWT."""
    return {
        "message": f"Hello, {request.jwt_identity}!",
        "claims": request.jwt_claims,
    }


@app.get("/fresh-only")
@fresh_jwt_required
def fresh_only(request):
    """Route that requires a fresh token (from login, not refresh)."""
    return {
        "message": "This route requires a fresh token",
        "user": request.jwt_identity,
    }


@app.post("/refresh")
@jwt_refresh_token_required
def refresh(request):
    """Get a new access token using refresh token."""
    # Create new access token (not fresh since it's from refresh)
    new_access_token = jwt.create_access_token(
        identity=request.jwt_identity,
        fresh=False,
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


@app.get("/public")
def public():
    """Public route - no authentication required."""
    return {"message": "This is a public endpoint"}


if __name__ == "__main__":
    print("JWT Authentication Example")
    print("-" * 40)
    print("Endpoints:")
    print("  POST /login          - Get tokens")
    print("  GET  /protected      - Requires JWT")
    print("  GET  /fresh-only     - Requires fresh JWT")
    print("  POST /refresh        - Refresh access token")
    print("  GET  /public         - No auth required")
    print("-" * 40)
    app.run(debug=True)
