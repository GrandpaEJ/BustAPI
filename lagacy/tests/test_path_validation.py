"""
Tests for Path parameter validation in BustAPI.
"""

import os
import sys

# Add python directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

import pytest
from bustapi import BustAPI, Path
from bustapi.testing import TestClient


class TestPathValidation:
    """Test suite for Path parameter validation."""

    def test_numeric_ge_constraint(self):
        """Test greater-than-or-equal-to constraint for numeric parameters."""
        app = BustAPI()

        @app.route("/users/<int:user_id>")
        def get_user(user_id: int = Path(ge=1)):
            return {"user_id": user_id}

        client = TestClient(app)

        # Valid: user_id >= 1
        response = client.get("/users/1")
        assert response.status_code == 200
        assert response.json["user_id"] == 1

        response = client.get("/users/100")
        assert response.status_code == 200
        assert response.json["user_id"] == 100

        # Invalid: user_id < 1
        response = client.get("/users/0")
        assert response.status_code == 400
        assert (
            "Validation error" in response.text
            or "must be greater than or equal" in response.text
        )

    def test_numeric_le_constraint(self):
        """Test less-than-or-equal-to constraint for numeric parameters."""
        app = BustAPI()

        @app.route("/items/<int:item_id>")
        def get_item(item_id: int = Path(le=1000)):
            return {"item_id": item_id}

        client = TestClient(app)

        # Valid: item_id <= 1000
        response = client.get("/items/1000")
        assert response.status_code == 200

        response = client.get("/items/500")
        assert response.status_code == 200

        # Invalid: item_id > 1000
        response = client.get("/items/1001")
        assert response.status_code == 400

    def test_numeric_range_constraint(self):
        """Test combined ge and le constraints."""
        app = BustAPI()

        @app.route("/products/<int:product_id>")
        def get_product(product_id: int = Path(ge=1, le=100)):
            return {"product_id": product_id}

        client = TestClient(app)

        # Valid: 1 <= product_id <= 100
        response = client.get("/products/1")
        assert response.status_code == 200

        response = client.get("/products/50")
        assert response.status_code == 200

        response = client.get("/products/100")
        assert response.status_code == 200

        # Invalid: product_id < 1
        response = client.get("/products/0")
        assert response.status_code == 400

        # Invalid: product_id > 100
        response = client.get("/products/101")
        assert response.status_code == 400

    def test_numeric_gt_lt_constraints(self):
        """Test strict greater-than and less-than constraints."""
        app = BustAPI()

        @app.route("/values/<int:value>")
        def get_value(value: int = Path(gt=0, lt=10)):
            return {"value": value}

        client = TestClient(app)

        # Valid: 0 < value < 10
        response = client.get("/values/1")
        assert response.status_code == 200

        response = client.get("/values/5")
        assert response.status_code == 200

        response = client.get("/values/9")
        assert response.status_code == 200

        # Invalid: value <= 0
        response = client.get("/values/0")
        assert response.status_code == 400

        # Invalid: value >= 10
        response = client.get("/values/10")
        assert response.status_code == 400

    def test_string_min_length(self):
        """Test minimum length constraint for string parameters."""
        app = BustAPI()

        @app.route("/tags/<tag>")
        def get_tag(tag: str = Path(min_length=3)):
            return {"tag": tag}

        client = TestClient(app)

        # Valid: len(tag) >= 3
        response = client.get("/tags/abc")
        assert response.status_code == 200

        response = client.get("/tags/python")
        assert response.status_code == 200

        # Invalid: len(tag) < 3
        response = client.get("/tags/ab")
        assert response.status_code == 400

    def test_string_max_length(self):
        """Test maximum length constraint for string parameters."""
        app = BustAPI()

        @app.route("/slugs/<slug>")
        def get_slug(slug: str = Path(max_length=10)):
            return {"slug": slug}

        client = TestClient(app)

        # Valid: len(slug) <= 10
        response = client.get("/slugs/hello")
        assert response.status_code == 200

        response = client.get("/slugs/1234567890")
        assert response.status_code == 200

        # Invalid: len(slug) > 10
        response = client.get("/slugs/12345678901")
        assert response.status_code == 400

    def test_string_length_range(self):
        """Test combined min and max length constraints."""
        app = BustAPI()

        @app.route("/usernames/<username>")
        def get_username(username: str = Path(min_length=3, max_length=20)):
            return {"username": username}

        client = TestClient(app)

        # Valid: 3 <= len(username) <= 20
        response = client.get("/usernames/abc")
        assert response.status_code == 200

        response = client.get("/usernames/john_doe")
        assert response.status_code == 200

        response = client.get("/usernames/12345678901234567890")
        assert response.status_code == 200

        # Invalid: len(username) < 3
        response = client.get("/usernames/ab")
        assert response.status_code == 400

        # Invalid: len(username) > 20
        response = client.get("/usernames/123456789012345678901")
        assert response.status_code == 400

    def test_regex_pattern(self):
        """Test regex pattern matching constraint."""
        app = BustAPI()

        @app.route("/codes/<code>")
        def get_code(code: str = Path(regex=r"^[A-Z]{3}-\d{4}$")):
            return {"code": code}

        client = TestClient(app)

        # Valid: matches pattern
        response = client.get("/codes/ABC-1234")
        assert response.status_code == 200

        response = client.get("/codes/XYZ-9999")
        assert response.status_code == 200

        # Invalid: doesn't match pattern
        response = client.get("/codes/abc-1234")  # lowercase
        assert response.status_code == 400

        response = client.get("/codes/AB-1234")  # too few letters
        assert response.status_code == 400

        response = client.get("/codes/ABC-123")  # too few digits
        assert response.status_code == 400

    def test_multiple_parameters(self):
        """Test multiple parameters with different constraints."""
        app = BustAPI()

        @app.route("/items/<int:item_id>/quantity/<int:qty>")
        def update_quantity(item_id: int = Path(ge=1), qty: int = Path(ge=1, le=100)):
            return {"item_id": item_id, "quantity": qty}

        client = TestClient(app)

        # Both valid
        response = client.get("/items/5/quantity/10")
        assert response.status_code == 200
        data = response.json
        assert data["item_id"] == 5
        assert data["quantity"] == 10

        # item_id invalid
        response = client.get("/items/0/quantity/10")
        assert response.status_code == 400

        # qty invalid (too high)
        response = client.get("/items/5/quantity/101")
        assert response.status_code == 400

        # qty invalid (too low)
        response = client.get("/items/5/quantity/0")
        assert response.status_code == 400

    def test_float_validation(self):
        """Test validation with float parameters."""
        app = BustAPI()

        @app.route("/prices/<float:price>")
        def check_price(price: float = Path(ge=0.01, le=999.99)):
            return {"price": price}

        client = TestClient(app)

        # Valid prices
        response = client.get("/prices/0.01")
        assert response.status_code == 200

        response = client.get("/prices/19.99")
        assert response.status_code == 200

        response = client.get("/prices/999.99")
        assert response.status_code == 200

        # Invalid: too low
        response = client.get("/prices/0.00")
        assert response.status_code == 400

        # Invalid: too high
        response = client.get("/prices/1000.00")
        assert response.status_code == 400

    def test_no_validation_without_path(self):
        """Test that routes without Path constraints work normally."""
        app = BustAPI()

        @app.route("/users/<int:user_id>")
        def get_user(user_id: int):
            return {"user_id": user_id}

        client = TestClient(app)

        # Should work with any valid integer
        response = client.get("/users/0")
        assert response.status_code == 200

        response = client.get("/users/999999")
        assert response.status_code == 200

    def test_validation_error_message(self):
        """Test that validation errors have descriptive messages."""
        app = BustAPI()

        @app.route("/users/<int:user_id>")
        def get_user(user_id: int = Path(ge=1, le=1000, description="User ID")):
            return {"user_id": user_id}

        client = TestClient(app)

        response = client.get("/users/0")
        assert response.status_code == 400
        # Should contain parameter name in error message
        assert (
            "user_id" in response.text.lower() or "validation" in response.text.lower()
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
