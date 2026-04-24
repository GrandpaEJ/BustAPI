import asyncio

from bustapi import BustAPI
from bustapi.safe import Array, Boolean, Const, Float, Integer, String, Struct, py

app = BustAPI()

# --- Data Models with New Types ---


class Product(Struct):
    id: Integer
    name: String
    price: Float
    in_stock: Boolean
    tags: Array(String)  # List of Strings
    rating: Array(Float)  # List of Floats


class Cart(Struct):
    user_id: Integer
    items: Array(Product)  # Nested List of Structs!


# --- Handlers ---


@app.route("/checkout", methods=["POST"])
async def checkout():
    # Simulated JSON payload
    data = {
        "user_id": 42,
        "items": [
            {
                "id": 101,
                "name": "Rust Book",
                "price": 49.99,
                "in_stock": True,
                "tags": ["book", "programming", "rust"],
                "rating": [4.5, 5.0, 4.8],
            },
            {
                "id": 102,
                "name": "Python Coffee Mug",
                "price": 12.50,
                "in_stock": True,
                "tags": ["swag", "mug"],
                "rating": [4.0],
            },
        ],
    }

    try:
        # Full recursive validation of Lists, nested structs, and types
        cart = Cart(**data)

        total = 0.0
        for item in cart.items:
            print(f"🛒 Item: {item.name} (${item.price}) - Tags: {item.tags}")
            total += item.price

        return {"status": "success", "total": total, "items_count": len(cart.items)}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    app.run(port=5000)
