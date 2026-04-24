"""
Example demonstrating Path parameter validation in BustAPI.

This example shows how to use the Path() helper to add validation
constraints to route path parameters.
"""

from bustapi import BustAPI, Path, jsonify

app = BustAPI()


@app.route("/users/<int:user_id>")
def get_user(
    user_id: int = Path(ge=1, le=1000, description="User ID between 1 and 1000"),
):
    """
    Get user by ID with validation.

    Valid IDs: 1-1000
    Invalid IDs will return 400 Bad Request
    """
    return jsonify({"user_id": user_id, "name": f"User {user_id}", "status": "active"})


@app.route("/products/<int:product_id>")
def get_product(
    product_id: int = Path(gt=0, description="Product ID must be positive"),
):
    """
    Get product by ID.

    Product ID must be greater than 0.
    """
    return jsonify(
        {"product_id": product_id, "name": f"Product {product_id}", "price": 99.99}
    )


@app.route("/posts/<slug>")
def get_post(slug: str = Path(min_length=3, max_length=50, description="Post slug")):
    """
    Get post by slug with length validation.

    Slug must be between 3 and 50 characters.
    """
    return jsonify(
        {
            "slug": slug,
            "title": f"Post: {slug}",
            "content": "Lorem ipsum dolor sit amet...",
        }
    )


@app.route("/tags/<tag_name>")
def get_tag(
    tag_name: str = Path(
        regex=r"^[a-z0-9-]+$",
        description="Tag name (lowercase alphanumeric with hyphens)",
    ),
):
    """
    Get tag with regex validation.

    Tag name must be lowercase alphanumeric with hyphens only.
    Valid: "python-web", "api-design", "rust"
    Invalid: "Python", "API_Design", "C++"
    """
    return jsonify({"tag": tag_name, "posts_count": 42})


@app.route("/prices/<float:price>")
def check_price(
    price: float = Path(
        ge=0.01, le=999999.99, description="Price between $0.01 and $999,999.99"
    ),
):
    """
    Check price with range validation.

    Price must be between 0.01 and 999999.99.
    """
    return jsonify({"price": price, "formatted": f"${price:,.2f}", "valid": True})


@app.route("/items/<int:item_id>/quantity/<int:qty>")
def update_quantity(
    item_id: int = Path(ge=1, description="Item ID"),
    qty: int = Path(ge=1, le=100, description="Quantity (1-100)"),
):
    """
    Update item quantity with multiple validated parameters.

    Both item_id and quantity have their own validation rules.
    """
    return jsonify({"item_id": item_id, "quantity": qty, "updated": True})


@app.errorhandler(400)
def bad_request(error):
    """Custom error handler for validation errors."""
    return jsonify({"error": "Bad Request", "message": str(error), "status": 400}), 400


if __name__ == "__main__":
    print("🚀 Path Validation Example")
    print("=" * 60)
    print("\nTry these URLs:")
    print("  Valid:")
    print("    http://127.0.0.1:5020/users/123")
    print("    http://127.0.0.1:5020/products/42")
    print("    http://127.0.0.1:5020/posts/hello-world")
    print("    http://127.0.0.1:5020/tags/python-web")
    print("    http://127.0.0.1:5020/prices/19.99")
    print("    http://127.0.0.1:5020/items/5/quantity/10")
    print("\n  Invalid (will return 400):")
    print("    http://127.0.0.1:5020/users/0       (too low)")
    print("    http://127.0.0.1:5020/users/9999    (too high)")
    print("    http://127.0.0.1:5020/posts/ab      (too short)")
    print("    http://127.0.0.1:5020/tags/Python   (uppercase not allowed)")
    print("    http://127.0.0.1:5020/prices/0      (too low)")
    print("    http://127.0.0.1:5020/items/5/quantity/200  (quantity too high)")
    print("\n" + "=" * 60)

    app.run(port=5020, workers=4, debug=True)
