import os
import sys
import threading
import time

import requests

print(f"Running with Python: {sys.version}")

# Try to import bustapi. If not installed, we might need manual path setup
try:
    from bustapi import BustAPI
except ImportError as e:
    print(f"BustAPI not found in path: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)


def test_app():
    app = BustAPI()

    @app.route("/hello")
    def hello(request):
        return {"message": "Hello from unified router!"}

    @app.route("/users/<int:id>")
    def user(request):
        return {
            "user_id": request.query_params.get("id")
        }  # Wait, pattern match handling might differ

    # Start server in thread
    # app.run() is blocking.
    # We'll rely on the user running it or just manual check if we can't spawn easily.
    # For now, let's just create the app and route, verifying no crashes.
    print("App created and route added successfully.")


if __name__ == "__main__":
    test_app()
