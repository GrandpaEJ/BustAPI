"""
Example of optional documentation support in BustAPI.

This example shows how to add Swagger UI and ReDoc to a BustAPI application
using the BustAPIDocs extension.
"""

from bustapi import BustAPI
from bustapi.docs import BustAPIDocs

app = BustAPI()

# Initialize optional docs
docs = BustAPIDocs(
    app,
    title="My Awesome API",
    version="1.0.0",
    description="This is a sample API with optional documentation.",
    docs_url="/api/docs",  # Custom URL for Swagger UI
)


@app.route("/")
def hello():
    """
    Root endpoint.
    
    Returns a simple hello message.
    """
    return {"message": "Hello, World!"}


@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    """
    Get user by ID.
    
    Args:
        user_id: The ID of the user to retrieve.
    """
    return {"id": user_id, "name": "John Doe"}


@app.route("/items", methods=["POST"])
def create_item():
    """
    Create a new item.
    
    This endpoint accepts JSON data to create an item.
    """
    return {"status": "created"}, 201


if __name__ == "__main__":
    print("🚀 Starting server with docs...")
    print(f"📄 Swagger UI: http://127.0.0.1:5000{docs.docs_url}")
    print(f"📚 ReDoc: http://127.0.0.1:5000{docs.redoc_url}")
    app.run(debug=True)
