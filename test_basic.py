#!/usr/bin/env python3
"""
Basic test to verify BustAPI functionality
"""

def test_import():
    """Test that we can import BustAPI"""
    try:
        from bustapi import BustAPI, jsonify, request
        print("[OK] Import successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False


def test_app_creation():
    """Test that we can create a BustAPI app"""
    try:
        from bustapi import BustAPI
        app = BustAPI()
        print("[OK] App creation successful")
        return True
    except Exception as e:
        print(f"[FAIL] App creation failed: {e}")
        return False


def test_route_decoration():
    """Test that we can add routes"""
    try:
        from bustapi import BustAPI
        app = BustAPI()

        @app.route('/')
        def hello():
            return {'message': 'Hello, World!'}

        @app.get('/test')
        def test():
            return 'Test endpoint'

        print("[OK] Route decoration successful")
        return True
    except Exception as e:
        print(f"[FAIL] Route decoration failed: {e}")
        return False


def test_flask_compatibility():
    """Test Flask compatibility layer"""
    try:
        from bustapi import Flask  # Flask alias
        app = Flask(__name__)

        @app.route('/compat')
        def compat():
            return {'flask_compatible': True}

        print("[OK] Flask compatibility successful")
        return True
    except Exception as e:
        print(f"[FAIL] Flask compatibility failed: {e}")
        return False


def main():
    """Run all basic tests"""
    print("Testing BustAPI Basic Functionality")
    print("=" * 40)

    tests = [
        test_import,
        test_app_creation,
        test_route_decoration,
        test_flask_compatibility,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("All basic tests passed! BustAPI is working correctly.")
        return True
    else:
        print("Some tests failed. Check the output above.")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)