#!/usr/bin/env python3
"""
Basic Hello World Example

This is the simplest possible BustAPI application.
It demonstrates:
- Creating a BustAPI app
- Defining a route
- Returning a response
- Running the development server
"""

from bustapi import BustAPI

# Create the BustAPI application instance
app = BustAPI()


@app.route("/")
def hello_world():
    """
    Simple hello world endpoint.

    Returns:
        dict: JSON response with greeting message
    """
    return {"message": "Hello, World!", "framework": "BustAPI"}


@app.route("/hello/<name>")
def hello_name(name):
    """
    Personalized greeting endpoint.

    Args:
        name (str): Name from URL parameter

    Returns:
        dict: JSON response with personalized greeting
    """
    return {"message": f"Hello, {name}!", "framework": "BustAPI", "name": name}


@app.route("/info")
def app_info():
    """
    Application information endpoint.

    Returns:
        dict: Information about the application
    """
    return {
        "name": "BustAPI Hello World",
        "version": "1.0.0",
        "description": "A simple BustAPI application",
        "endpoints": [
            "/ - Hello World",
            "/hello/<name> - Personalized greeting",
            "/info - Application information",
        ],
    }


if __name__ == "__main__":
    print("🚀 Starting BustAPI Hello World application...")
    print("📍 Visit: http://127.0.0.1:8000")
    print("📍 Try: http://127.0.0.1:8000/hello/YourName")
    print("📍 Info: http://127.0.0.1:8000/info")

    # Run the development server
    app.run(host="127.0.0.1", port=8000, debug=True)
