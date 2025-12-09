# Auto-Documentation

BustAPI can automatically generate OpenAPI (Swagger) documentation for your API.

## Setup

```python
from bustapi import BustAPI, BustAPIDocs

app = BustAPI()
docs = BustAPIDocs(app)  # Initialize docs extension

@app.route("/item/<int:id>")
def get_item(request, id: int):
    """
    Get an item by ID.
    ---
    responses:
      200:
        description: Item found
    """
    return {"id": id}

if __name__ == "__main__":
    app.run()
```

## Accessing Docs

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`
