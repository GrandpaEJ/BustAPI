from bustapi import BustAPI, BustAPIDocs

app = BustAPI()

# Initialize auto-documentation
docs = BustAPIDocs(
    app,
    title="My Documented API",
    version="1.0.0",
    description="This API demonstrates automatic OpenAPI documentation generation.",
)


@app.route("/items")
def get_items():
    """
    Get a list of items.

    Returns a list of strings representing items in the inventory.
    """
    return ["item1", "item2"]


@app.route("/items/<int:item_id>")
def get_item(item_id):
    """
    Get a specific item by ID.

    Args:
        item_id: The ID of the item to retrieve.
    """
    return {"id": item_id, "name": f"Item {item_id}"}


@app.post("/items")
def create_item():
    """
    Create a new item.
    """
    return {"id": 3, "name": "New Item"}


if __name__ == "__main__":
    print("Running auto-docs example on http://127.0.0.1:5007")
    print("Swagger UI: http://127.0.0.1:5007/docs")
    print("ReDoc:      http://127.0.0.1:5007/redoc")
    print("OpenAPI:    http://127.0.0.1:5007/openapi.json")
    app.run(port=5007, debug=True)
