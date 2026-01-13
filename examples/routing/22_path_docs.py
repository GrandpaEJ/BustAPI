"""
Example demonstrating FastAPI-compatible Path documentation in BustAPI.

This example shows how Path parameters are automatically documented
in the OpenAPI schema with full validation constraints.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from bustapi import BustAPI, Path
from bustapi.documentation import BustAPIDocs

app = BustAPI()

# Initialize documentation
docs = BustAPIDocs(
    app,
    title="BustAPI Path Documentation Demo",
    version="1.0.0",
    description="Demonstration of FastAPI-compatible Path parameter documentation",
)


@app.route("/users/<int:user_id>")
def get_user(
    user_id: int = Path(
        ge=1, le=1000, description="The unique identifier for the user", example=123
    ),
):
    """
    Get user by ID.

    Retrieves a user's information using their unique ID.
    """
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
    }


@app.route("/products/<int:product_id>")
def get_product(
    product_id: int = Path(
        gt=0,
        description="Product ID (must be positive)",
        title="Product ID",
        example=42,
    ),
):
    """
    Get product details.

    Fetch detailed information about a specific product.
    """
    return {
        "product_id": product_id,
        "name": f"Product {product_id}",
        "price": 99.99,
        "in_stock": True,
    }


@app.route("/posts/<slug>")
def get_post(
    slug: str = Path(
        min_length=3,
        max_length=50,
        regex=r"^[a-z0-9-]+$",
        description="URL-friendly post identifier (lowercase alphanumeric with hyphens)",
        example="my-first-post",
    ),
):
    """
    Get blog post by slug.

    Retrieve a blog post using its URL-friendly slug identifier.
    """
    return {
        "slug": slug,
        "title": f"Post: {slug.replace('-', ' ').title()}",
        "content": "Lorem ipsum dolor sit amet...",
        "published": True,
    }


@app.route("/prices/<float:amount>")
def check_price(
    amount: float = Path(
        ge=0.01,
        le=999999.99,
        description="Price amount in USD",
        example=19.99,
        title="Price Amount",
    ),
):
    """
    Validate price amount.

    Check if a price amount is within acceptable range.
    """
    return {
        "amount": amount,
        "formatted": f"${amount:,.2f}",
        "currency": "USD",
        "valid": True,
    }


@app.route("/tags/<tag>")
def get_tag(
    tag: str = Path(
        regex=r"^[a-z0-9-]+$",
        min_length=2,
        max_length=30,
        description="Tag name (lowercase, alphanumeric with hyphens)",
        examples=["python", "web-dev", "api-design"],
        deprecated=False,
    ),
):
    """
    Get posts by tag.

    Retrieve all posts associated with a specific tag.
    """
    return {"tag": tag, "posts_count": 42, "posts": []}


@app.route("/items/<int:item_id>/reviews/<int:review_id>")
def get_review(
    item_id: int = Path(ge=1, description="Item ID", example=5),
    review_id: int = Path(ge=1, description="Review ID", example=123),
):
    """
    Get a specific review for an item.

    Retrieve detailed information about a particular review.
    """
    return {
        "item_id": item_id,
        "review_id": review_id,
        "rating": 5,
        "comment": "Great product!",
    }


if __name__ == "__main__":
    print("🚀 FastAPI-Compatible Path Documentation Demo")
    print("=" * 60)
    print("\nDocumentation URLs:")
    print("  Swagger UI:  http://127.0.0.1:5021/docs")
    print("  ReDoc:       http://127.0.0.1:5021/redoc")
    print("  OpenAPI:     http://127.0.0.1:5021/openapi.json")
    print("\nAPI Endpoints:")
    print("  GET /users/123")
    print("  GET /products/42")
    print("  GET /posts/my-first-post")
    print("  GET /prices/19.99")
    print("  GET /tags/python")
    print("  GET /items/5/reviews/123")
    print("\n" + "=" * 60)
    print("\nCheck the Swagger UI to see Path validation constraints!")
    print("All parameters show:")
    print("  - Type (integer, number, string)")
    print("  - Constraints (minimum, maximum, pattern, etc.)")
    print("  - Descriptions and examples")
    print("=" * 60)

    app.run(port=5021, workers=2, debug=True)
