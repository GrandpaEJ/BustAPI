#!/usr/bin/env python3
"""
Simple Working Flask Extensions Demo

This demonstrates Flask extensions that work perfectly with BustAPI:
✅ Flask-CORS: Cross-Origin Resource Sharing
✅ Flask-JWT-Extended: JWT Authentication
"""

from bustapi import BustAPI

app = BustAPI()

# Configure Flask-CORS
try:
    from flask_cors import CORS

    CORS(app, origins=["http://localhost:3000"])
    cors_available = True
    print("✅ Flask-CORS initialized successfully")
except ImportError:
    cors_available = False
    print("⚠️ Flask-CORS not available")

# Configure Flask-JWT-Extended
try:
    from flask_jwt_extended import JWTManager, create_access_token

    app.config["JWT_SECRET_KEY"] = "demo-secret-key"
    jwt = JWTManager(app)
    jwt_available = True
    print("✅ Flask-JWT-Extended initialized successfully")
except ImportError:
    jwt_available = False
    print("⚠️ Flask-JWT-Extended not available")


@app.route("/")
def index():
    """Main demo page"""
    return {
        "message": "BustAPI Flask Extensions Demo",
        "extensions": {
            "flask_cors": cors_available,
            "flask_jwt_extended": jwt_available,
        },
        "endpoints": [
            "GET / - This page",
            "GET /demo/cors - CORS demo",
            "POST /demo/login - Get JWT token",
            "GET /demo/status - Extension status",
        ],
    }


@app.route("/demo/cors")
def cors_demo():
    """CORS-enabled endpoint"""
    return {
        "message": "This endpoint has CORS enabled",
        "cors_enabled": cors_available,
        "note": "Check response headers for CORS headers",
    }


@app.route("/demo/login", methods=["POST"])
def demo_login():
    """Simple login that returns JWT token"""
    if not jwt_available:
        return {"error": "JWT not available"}, 500

    # Create a demo token
    token = create_access_token(identity="demo-user")
    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "Bearer",
    }


@app.route("/demo/status")
def status():
    """Show extension status"""
    return {
        "bustapi_version": "0.1.0",
        "extensions_status": {
            "flask_cors": {
                "available": cors_available,
                "status": "Working" if cors_available else "Not installed",
            },
            "flask_jwt_extended": {
                "available": jwt_available,
                "status": "Working" if jwt_available else "Not installed",
            },
        },
        "compatibility_rate": f"{((cors_available + jwt_available) / 2 * 100):.0f}%",
    }


if __name__ == "__main__":
    print("\n🚀 BustAPI Flask Extensions Demo")
    print("=" * 40)
    print("📍 http://127.0.0.1:8000")
    print("📍 http://127.0.0.1:8000/demo/status")
    print("📍 http://127.0.0.1:8000/demo/cors")
    print("📍 POST http://127.0.0.1:8000/demo/login")
    print("=" * 40)

    app.run(host="127.0.0.1", port=8000, debug=True)
