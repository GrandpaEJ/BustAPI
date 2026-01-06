# Request Data

Data enters your application from the client in various forms: URL parameters, query strings, headers, and body payloads. BustAPI provides multiple ways to access this data.

## The `request` Proxy

For direct, imperative access to request data, use the global `request` object. This object is a thread-safe proxy that always points to the incoming request for the current context.

### Query Strings

To access URL parameters like `?key=value`, use the `args` attribute:

```python
from bustapi import request

@app.route("/search")
def search():
    search_query = request.args.get("q", "")
    return f"Searching for {search_query}"
```

### Form Data

To access form data from POST requests, use the `form` attribute:

```python
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    return "Logged in"
```

### JSON Data

For API endpoints receiving JSON, use `get_json()`:

```python
@app.post("/api/data")
def api_data():
    data = request.get_json()
    # data is now a standard Python dictionary
    return data
```

!!! warning "Error Handling"
    If the request content-type is `application/json` but the body is malformed, `get_json()` may raise a 404/400 error. You can pass `force=True` to ignore content-type.

### Async Body Access

For high-performance applications, you might want to stream the request body or read it asynchronously.

```python
@app.post("/upload")
async def upload():
    # Read entire body as bytes (async)
    body_bytes = await request.body()
    
    # Or stream chunks (async generator)
    async for chunk in request.stream():
        process_chunk(chunk)
        
    return "Uploaded"
```

## Type-Safe Injection (Recommended)

While the `request` object is useful, the "modern" way to handle data in BustAPI is via function parameter injection. This provides auto-validation and clearer function signatures.

### Query Injection and Keyword Arguments

You can accept query parameters directly as keyword arguments in your handler function. BustAPI automatically maps `?limit=10` to the `limit` argument.

```python
@app.get("/items")
def items(limit=10, offset=0):
    # ?limit=20&offset=5 -> limit="20", offset="5" (strings)
    return f"Items {limit}, {offset}"
```

For type safety and validation, use the `Query` marker (similar to FastAPI):

```python
from bustapi import Query

@app.get("/validated")
def validated(limit: int = Query(10)):
    # limit and offset are automatically converted to int
    return f"Showing items {offset} to {offset + limit}"
```

### Body Injection

Use the `Body` marker to declare a JSON body requirement.

```python
from bustapi import Body

@app.post("/items")
def create_item(payload: dict = Body(...)):
    # payload is guaranteed to be a dict
    # '...' means it is required
    return payload
```
