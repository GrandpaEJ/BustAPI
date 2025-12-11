#!/usr/bin/env python3
"""
Test script to verify all examples work correctly.
Tests each example by starting the server and making requests to all endpoints.
"""

import signal
import subprocess
import sys
import time

import requests


def test_example(example_file, port, tests):
    """Test an example by starting it and making requests."""
    print(f"\n{'=' * 60}")
    print(f"Testing: {example_file}")
    print(f"{'=' * 60}")

    # Start the server
    proc = subprocess.Popen(
        [sys.executable, example_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait for server to start
    time.sleep(3)

    try:
        # Run tests
        passed = 0
        failed = 0

        for test_name, method, url, data, headers, expected_status in tests:
            try:
                if method == "GET":
                    response = requests.get(url, timeout=5)
                elif method == "POST":
                    response = requests.post(url, json=data, headers=headers, timeout=5)
                elif method == "PUT":
                    response = requests.put(url, json=data, headers=headers, timeout=5)
                else:
                    response = requests.request(
                        method, url, json=data, headers=headers, timeout=5
                    )

                if response.status_code == expected_status:
                    print(f"  ✓ {test_name}: {response.status_code}")
                    passed += 1
                else:
                    print(
                        f"  ✗ {test_name}: Expected {expected_status}, got {response.status_code}"
                    )
                    print(f"    Response: {response.text[:200]}")
                    failed += 1
            except Exception as e:
                print(f"  ✗ {test_name}: {str(e)}")
                failed += 1

        print(f"\nResults: {passed} passed, {failed} failed")
        return failed == 0

    finally:
        # Stop the server
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)


# Test Body and Depends example
body_depends_tests = [
    # Body validation
    (
        "Valid user creation",
        "POST",
        "http://localhost:5023/users",
        {"name": "Alice", "email": "alice@example.com", "age": 30},
        {"Content-Type": "application/json"},
        200,
    ),
    (
        "Invalid user (bad email)",
        "POST",
        "http://localhost:5023/users",
        {"name": "Bob", "email": "invalid", "age": 25},
        {"Content-Type": "application/json"},
        400,
    ),
    (
        "Invalid user (age too high)",
        "POST",
        "http://localhost:5023/users",
        {"name": "Charlie", "email": "charlie@example.com", "age": 200},
        {"Content-Type": "application/json"},
        400,
    ),
    # Dependency injection
    (
        "Profile with valid token",
        "GET",
        "http://localhost:5023/profile?token=secret",
        None,
        {},
        200,
    ),
    (
        "Profile with invalid token",
        "GET",
        "http://localhost:5023/profile?token=invalid",
        None,
        {},
        401,
    ),
    (
        "Admin users with valid token",
        "GET",
        "http://localhost:5023/admin/users?token=secret",
        None,
        {},
        200,
    ),
    (
        "Admin users with user token",
        "GET",
        "http://localhost:5023/admin/users?token=user123",
        None,
        {},
        403,
    ),
    # Combined Body + Depends
    (
        "Admin create user",
        "POST",
        "http://localhost:5023/admin/users/create?token=secret",
        {"name": "NewUser", "email": "newuser@example.com", "role": "user"},
        {"Content-Type": "application/json"},
        200,
    ),
]

if __name__ == "__main__":
    print("🧪 Testing BustAPI Examples")
    print("=" * 60)

    all_passed = True

    # Test Body and Depends example
    if not test_example("examples/24_body_and_depends.py", 5023, body_depends_tests):
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All example tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
