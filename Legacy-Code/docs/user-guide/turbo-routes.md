# Turbo Routes

Turbo routes are BustAPI's fastest route type, designed for maximum throughput on simple endpoints.

## Overview

Regular routes go through Python's full request lifecycle:
- Request object creation
- Context variable setup
- Session handling
- Middleware execution
- Parameter extraction

**Turbo routes skip all of this.** Path parameters are parsed and extracted entirely in Rust (new in **v0.9.0**) and passed directly to your handler. This results in zero Python-side regex overhead.

## Performance

| Route Type | Requests/sec | Use Case |
|:---|---:|:---|
| Regular `@app.route()` | ~25,000 | Complex endpoints |
| Static `@app.turbo_route()` | ~34,000 | Health checks, static data |
| Dynamic `@app.turbo_route()` | ~30,000 | Simple lookups by ID |
| **Cached `@app.turbo_route(cache_ttl=60)`** | **~140,000** | Cached responses |

## Cached Turbo Routes

Add `cache_ttl` for maximum performance:

```python
@app.turbo_route("/", cache_ttl=60)  # Cache for 60 seconds
def home():
    return {"message": "Hello, World!"}

@app.turbo_route("/config", cache_ttl=300)  # Cache for 5 minutes
def config():
    return expensive_config_load()
```

See [Response Caching](caching.md) for details.

## Static Turbo Routes

For endpoints that take no parameters:

```python
from bustapi import BustAPI

app = BustAPI()

@app.turbo_route("/health")
def health():
    return {"status": "ok"}

@app.turbo_route("/api/version")
def version():
    return {"version": "1.0.0", "api": "v1"}
```

## Dynamic Turbo Routes

For endpoints with path parameters:

```python
# Integer parameter
@app.turbo_route("/users/<int:id>")
def get_user(id: int):
    return {"id": id, "name": f"User {id}"}

# String parameter
@app.turbo_route("/greet/<name>")
def greet(name: str):
    return {"message": f"Hello, {name}!"}

# Float parameter
@app.turbo_route("/calc/<float:value>")
def double(value: float):
    return {"result": value * 2}

# Multiple parameters
@app.turbo_route("/posts/<int:post_id>/comments/<int:comment_id>")
def get_comment(post_id: int, comment_id: int):
    return {"post_id": post_id, "comment_id": comment_id}
```

## Supported Types

| Type | Pattern | Example | Python Type |
|:---|:---|:---|:---|
| Integer | `<int:name>` | `/users/<int:id>` | `int` |
| Float | `<float:name>` | `/calc/<float:value>` | `float` |
| String | `<name>` or `<str:name>` | `/greet/<name>` | `str` |
| Path | `<path:name>` | `/files/<path:filepath>` | `str` (includes `/`) |

## Type Validation

If a request doesn't match the expected type, BustAPI returns a 404:

```bash
# Valid request
curl http://localhost:5000/users/42
# {"id": 42, "name": "User 42"}

# Invalid request (string instead of int)
curl http://localhost:5000/users/abc
# 404 Not Found
```

## Limitations

Turbo routes trade features for speed. They do **not** support:

| Feature | Available? | Alternative |
|:---|:---:|:---|
| Request object | ❌ | Use regular `@app.route()` |
| Query parameters | ❌ | Use regular `@app.route()` |
| Middleware | ❌ | Use regular `@app.route()` |
| Sessions | ❌ | Use regular `@app.route()` |
| Authentication | ❌ | Use regular `@app.route()` |
| Headers access | ❌ | Use regular `@app.route()` |

## When to Use Turbo Routes

✅ **Good for:**
- Health check endpoints (`/health`, `/ready`, `/live`)
- Simple data lookups (`/users/<id>`, `/products/<id>`)
- Metrics endpoints (`/metrics`, `/stats`)
- High-frequency read APIs
- Microservice internal APIs

❌ **Not suitable for:**
- Endpoints needing authentication
- Form submissions
- File uploads
- Endpoints using query parameters
- Complex business logic

## HTTP Methods

Turbo routes support all HTTP methods via the `methods` parameter:

```python
@app.turbo_route("/items/<int:id>", methods=["GET"])
def get_item(id: int):
    return {"id": id}

@app.turbo_route("/items/<int:id>", methods=["DELETE"])
def delete_item(id: int):
    return {"deleted": id}
```

## Return Types

Turbo routes support these return types:

```python
# Dictionary (→ JSON)
@app.turbo_route("/json")
def json_response():
    return {"hello": "world"}

# List (→ JSON array)
@app.turbo_route("/list")
def list_response():
    return [1, 2, 3]

# String (→ HTML)
@app.turbo_route("/html")
def html_response():
    return "<h1>Hello</h1>"

# Tuple (body, status, headers)
@app.turbo_route("/custom")
def custom_response():
    return ({"data": 1}, 201, {"X-Custom": "header"})
```

## Big Integers

Turbo routes handle arbitrarily large integers by falling back to Python's `int`:

```python
@app.turbo_route("/bignum/<int:n>")
def big_number(n: int):
    return {"n": n, "doubled": n * 2}
```

```bash
curl http://localhost:5000/bignum/99999999999999999999
# {"n": 99999999999999999999, "doubled": 199999999999999999998}
```

## Best Practices

1. **Use type hints** for clarity (even though parsing is done in Rust):
   ```python
   @app.turbo_route("/users/<int:id>")
   def get_user(id: int):  # Type hint matches route
       ...
   ```

2. **Keep handlers simple** - turbo routes are for fast, simple operations:
   ```python
   # Good
   @app.turbo_route("/users/<int:id>")
   def get_user(id: int):
       return USERS_CACHE.get(id, {"error": "not found"})
   
   # Bad - too complex, use regular route
   @app.turbo_route("/users/<int:id>")
   def get_user(id: int):
       user = db.query(User).filter(User.id == id).first()  # DB query
       if not user:
           raise HTTPException(404)
       return user.to_dict()
   ```

3. **Match parameter names** between route and handler:
   ```python
   # Good
   @app.turbo_route("/posts/<int:post_id>")
   def get_post(post_id: int):  # ✅ Names match
       ...
   
   # Bad
   @app.turbo_route("/posts/<int:post_id>")
   def get_post(id: int):  # ❌ Name mismatch
       ...
   ```
