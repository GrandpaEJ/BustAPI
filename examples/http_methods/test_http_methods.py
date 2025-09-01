#!/usr/bin/env python3
"""
Test script for HTTP Methods

This script tests all HTTP methods using the requests library.
Run this after starting the http_methods.py server.
"""

import sys

import requests

BASE_URL = "http://127.0.0.1:8000"


def test_get_users():
    """Test GET /users"""
    print("🔍 Testing GET /users...")
    response = requests.get(f"{BASE_URL}/users")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_get_user():
    """Test GET /users/1"""
    print("🔍 Testing GET /users/1...")
    response = requests.get(f"{BASE_URL}/users/1")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_post_user():
    """Test POST /users"""
    print("📝 Testing POST /users...")
    data = {"name": "Charlie", "email": "charlie@example.com"}
    response = requests.post(f"{BASE_URL}/users", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    return response.json().get("user", {}).get("id")


def test_put_user(user_id):
    """Test PUT /users/{user_id}"""
    print(f"✏️ Testing PUT /users/{user_id}...")
    data = {"name": "Charlie Updated", "email": "charlie.updated@example.com"}
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_patch_user(user_id):
    """Test PATCH /users/{user_id}"""
    print(f"🔧 Testing PATCH /users/{user_id}...")
    data = {"name": "Charlie Patched"}
    response = requests.patch(f"{BASE_URL}/users/{user_id}", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_head_user(user_id):
    """Test HEAD /users/{user_id}"""
    print(f"👤 Testing HEAD /users/{user_id}...")
    response = requests.head(f"{BASE_URL}/users/{user_id}")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Body length: {len(response.content)}")
    print()


def test_options_users():
    """Test OPTIONS /users"""
    print("⚙️ Testing OPTIONS /users...")
    response = requests.options(f"{BASE_URL}/users")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print(f"Allow header: {response.headers.get('Allow', 'Not set')}")
    print()


def test_options_user(user_id):
    """Test OPTIONS /users/{user_id}"""
    print(f"⚙️ Testing OPTIONS /users/{user_id}...")
    response = requests.options(f"{BASE_URL}/users/{user_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print(f"Allow header: {response.headers.get('Allow', 'Not set')}")
    print()


def test_delete_user(user_id):
    """Test DELETE /users/{user_id}"""
    print(f"🗑️ Testing DELETE /users/{user_id}...")
    response = requests.delete(f"{BASE_URL}/users/{user_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_demo_endpoint():
    """Test the demo endpoint with different methods"""
    print("🎭 Testing demo endpoint with different methods...")

    methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    for method in methods:
        print(f"  Testing {method}...")
        response = requests.request(method, f"{BASE_URL}/demo")
        print(f"    Status: {response.status_code}")
        if method != "HEAD" and response.content:
            print(f"    Response: {response.json()}")
        else:
            print(f"    Headers: {dict(response.headers)}")
    print()


def main():
    """Run all tests"""
    print("🚀 Starting HTTP Methods Tests...")
    print("Make sure the http_methods.py server is running on port 8000\n")

    try:
        # Test basic GET operations
        test_get_users()
        test_get_user()

        # Test POST to create a new user
        new_user_id = test_post_user()

        if new_user_id:
            # Test other methods with the new user
            test_put_user(new_user_id)
            test_patch_user(new_user_id)
            test_head_user(new_user_id)
            test_options_user(new_user_id)
            test_delete_user(new_user_id)

        # Test OPTIONS on collection
        test_options_users()

        # Test demo endpoint
        test_demo_endpoint()

        print("✅ All tests completed!")

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server.")
        print("Make sure the http_methods.py server is running:")
        print("python examples/http_methods/http_methods.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
