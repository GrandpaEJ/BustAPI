# Responses

BustAPI is flexible in what you can return from a view function. It attempts to smartly convert your return values into a valid HTTP response.

## Return Types

### Strings

Returning a plain string results in a `text/html` response with a `200 OK` status.

```python
@app.route("/")
def home():
    return "<h1>Hello</h1>"
```

### Dictionaries & Lists

Returning a dictionary or a list will automatically serialize it to JSON and set the content-type to `application/json`.

```python
@app.route("/api/user")
def user():
    return {"name": "Alice", "role": "admin"}
```

### Tuples

You can return a tuple in the form `(body, status)` or `(body, status, headers)`.

```python
@app.route("/created")
def created():
    return {"id": 123}, 201, {"X-Custom-Header": "foo"}
```

## The `make_response` Helper

For more control, wrap your content in a `Response` object.

```python
from bustapi import make_response

@app.route("/xml")
def xml():
    resp = make_response("<data>value</data>")
```

## Streaming Responses

You can stream data to the client using `StreamingResponse`. This supports both synchronous and asynchronous iterators.

```python
from bustapi import StreamingResponse
import asyncio

async def fast_stream():
    for i in range(10):
        yield f"Chunk {i}\n"
        await asyncio.sleep(0.1)

@app.route("/stream")
async def stream():
    return StreamingResponse(fast_stream(), media_type="text/plain")
```

## Redirections & Errors

Use the helper functions `redirect` and `abort`.

```python
from bustapi import redirect, abort

@app.route("/old")
def old():
    return redirect("/new")

@app.route("/protected")
def protected():
    if not is_authorized:
        abort(403, "You shall not pass!")
```
