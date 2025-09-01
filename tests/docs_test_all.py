#!/usr/bin/env python3
"""
Run all documentation tests to ensure all code examples work
"""

import os
import subprocess
import sys


def run_test_file(test_file):
    """Run a test file and return success status."""
    print(f"🧪 Running {test_file}...")

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__),
        )

        if result.returncode == 0:
            print(f"✅ {test_file} passed")
            return True
        else:
            print(f"❌ {test_file} failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"❌ {test_file} failed with exception: {e}")
        return False


def main():
    """Run all documentation tests."""
    print("🚀 Running All Documentation Tests")
    print("=" * 60)

    # List of all documentation test files
    test_files = [
        "docs_test_simple.py",
        "docs_test_api_reference.py",
        "docs_test_installation.py",
    ]

    passed = 0
    total = len(test_files)

    for test_file in test_files:
        if run_test_file(test_file):
            passed += 1
        print()

    print("=" * 60)
    print(f"📊 FINAL RESULTS: {passed}/{total} test suites passed")

    if passed == total:
        print("🎉 ALL DOCUMENTATION TESTS PASSED!")
        print("✅ All code examples in docs/ are working correctly")
        return True
    else:
        print(f"❌ {total - passed} test suites failed")
        print("⚠️ Some documentation examples may not be working")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
