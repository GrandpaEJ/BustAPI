#!/usr/bin/env python3
"""
Quick BustAPI benchmark testing all optimization features:
1. Radix tree router (O(log n) matching)
2. Rust session serialization
3. Pre-compiled route patterns with type validation
"""

from bustapi import BustAPI
from bustapi.bustapi_core import Signer


# Test Rust session serialization performance
def test_session_serialization():
    """Test the new Rust session encode/decode"""
    signer = Signer("supersecretkey123")

    # Test data
    session_data = {
        "user_id": 12345,
        "username": "testuser",
        "roles": ["admin", "user"],
        "preferences": {"theme": "dark", "lang": "en"},
        "logged_in": True,
    }

    # Encode (Dict → JSON → Base64 → Sign)
    import time

    iterations = 10000

    start = time.perf_counter()
    for _ in range(iterations):
        encoded = signer.encode_session("session", session_data)
    encode_time = time.perf_counter() - start

    # Decode (Verify → Base64 → JSON → Dict)
    start = time.perf_counter()
    for _ in range(iterations):
        decoded = signer.decode_session("session", encoded)
    decode_time = time.perf_counter() - start

    print(f"   Encode: {iterations / encode_time:,.0f} ops/sec")
    print(f"   Decode: {iterations / decode_time:,.0f} ops/sec")
    return encoded, decoded


app = BustAPI()


# Static routes - turbo (fastest)
@app.turbo_route("/")
def index():
    return "Hello, World!"


@app.turbo_route("/json")
def json_endpoint():
    return {"hello": "world"}


# Dynamic routes with pre-compiled type validation
@app.route("/user/<int:id>")
def user_by_id(id: int):
    return {"user_id": id}


@app.route("/user/<name>")
def user_by_name(name: str):
    return {"username": name}


@app.route("/product/<float:price>")
def product_price(price: float):
    return {"price": price}


@app.route("/files/<path:filepath>")
def serve_files(filepath: str):
    return {"filepath": filepath}


# Many routes to test radix tree performance
for i in range(50):

    @app.route(f"/api/v1/resource{i}/<int:id>")
    def resource_handler(id: int, num=i):
        return {"resource": num, "id": id}


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 BustAPI Quick Benchmark (All Optimizations)")
    print("=" * 60)

    print(f"\n📊 Routes registered: {len(app.url_map)}")
    print("   - Static turbo routes: 2")
    print("   - Dynamic typed routes: 4")
    print("   - API resource routes: 50")

    print("\n⚡ Testing Rust Session Serialization...")
    test_session_serialization()

    print("\n🌐 Starting server...")
    print("   Run: wrk -t4 -c100 -d10s http://127.0.0.1:8080/json")
    print("   Run: wrk -t4 -c100 -d10s http://127.0.0.1:8080/user/123")
    print("   Run: wrk -t4 -c100 -d10s http://127.0.0.1:8080/api/v1/resource25/999")

    app.run(host="127.0.0.1", port=8080, workers=4, debug=False)
