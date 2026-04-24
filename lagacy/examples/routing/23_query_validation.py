"""
Example demonstrating Query parameter validation in BustAPI.

This example shows how Query parameters are automatically validated
with type coercion, constraints, and default values.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from bustapi import BustAPI, Query
from bustapi.documentation import BustAPIDocs

app = BustAPI()

# Initialize documentation
docs = BustAPIDocs(
    app,
    title="BustAPI Query Validation Demo",
    version="1.0.0",
    description="Demonstration of Query parameter validation with type coercion",
)


@app.route("/search")
def search(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    page: int = Query(1, ge=1, le=100, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Results per page"),
):
    """
    Search with pagination.

    Demonstrates required and optional query parameters with validation.
    """
    return {
        "query": q,
        "page": page,
        "limit": limit,
        "results": [f"Result {i}" for i in range(1, min(limit + 1, 6))],
    }


@app.route("/users")
def list_users(
    active: bool = Query(True, description="Filter by active status"),
    min_age: int = Query(0, ge=0, le=150, description="Minimum age"),
    role: str = Query("user", regex=r"^(admin|user|guest)$", description="User role"),
):
    """
    List users with filters.

    Demonstrates boolean and regex validation.
    """
    return {
        "filters": {"active": active, "min_age": min_age, "role": role},
        "users": [
            {"id": 1, "name": "Alice", "age": 30, "role": role, "active": active},
            {"id": 2, "name": "Bob", "age": 25, "role": role, "active": active},
        ],
    }


@app.route("/products")
def list_products(
    category: str = Query(..., description="Product category"),
    min_price: float = Query(0.0, ge=0.0, description="Minimum price"),
    max_price: float = Query(None, ge=0.0, description="Maximum price"),
    in_stock: bool = Query(False, description="Only show in-stock items"),
):
    """
    List products with price range.

    Demonstrates float validation and optional parameters.
    """
    filters = {"category": category, "min_price": min_price, "in_stock": in_stock}
    if max_price is not None:
        filters["max_price"] = max_price

    return {
        "filters": filters,
        "products": [
            {"id": 1, "name": "Product A", "price": 19.99, "category": category},
            {"id": 2, "name": "Product B", "price": 29.99, "category": category},
        ],
    }


@app.route("/api/data")
def get_data(
    format: str = Query(
        "json", regex=r"^(json|xml|csv)$", description="Response format"
    ),
    fields: str = Query(None, description="Comma-separated field names"),
    sort: str = Query("id", description="Sort field"),
    order: str = Query("asc", regex=r"^(asc|desc)$", description="Sort order"),
):
    """
    Get data with formatting options.

    Demonstrates multiple string validations.
    """
    return {
        "format": format,
        "fields": fields.split(",") if fields else None,
        "sort": sort,
        "order": order,
        "data": [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}],
    }


@app.route("/analytics")
def analytics(
    start_date: str = Query(
        ..., regex=r"^\d{4}-\d{2}-\d{2}$", description="Start date (YYYY-MM-DD)"
    ),
    end_date: str = Query(
        ..., regex=r"^\d{4}-\d{2}-\d{2}$", description="End date (YYYY-MM-DD)"
    ),
    metric: str = Query("views", description="Metric to analyze"),
    granularity: str = Query(
        "day", regex=r"^(hour|day|week|month)$", description="Data granularity"
    ),
):
    """
    Get analytics data.

    Demonstrates date validation with regex patterns.
    """
    return {
        "period": {"start": start_date, "end": end_date},
        "metric": metric,
        "granularity": granularity,
        "data": [{"date": start_date, "value": 100}, {"date": end_date, "value": 150}],
    }


if __name__ == "__main__":
    print("🚀 Query Parameter Validation Demo")
    print("=" * 60)
    print("\nDocumentation URLs:")
    print("  Swagger UI:  http://127.0.0.1:5022/docs")
    print("  ReDoc:       http://127.0.0.1:5022/redoc")
    print("  OpenAPI:     http://127.0.0.1:5022/openapi.json")
    print("\nExample Requests:")
    print("  # Valid requests")
    print("  curl 'http://localhost:5022/search?q=python&page=1&limit=10'")
    print("  curl 'http://localhost:5022/users?active=true&min_age=18&role=admin'")
    print(
        "  curl 'http://localhost:5022/products?category=electronics&min_price=10&max_price=100'"
    )
    print("\n  # Validation errors (400 responses)")
    print("  curl 'http://localhost:5022/search?page=-1'  # page must be >= 1")
    print("  curl 'http://localhost:5022/users?min_age=200'  # age must be <= 150")
    print(
        "  curl 'http://localhost:5022/users?role=invalid'  # role must match pattern"
    )
    print("\n" + "=" * 60)
    print("\nCheck Swagger UI to see query parameter constraints!")
    print("=" * 60)

    app.run(port=5022, workers=2, debug=True)
