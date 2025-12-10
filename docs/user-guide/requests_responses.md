# Requests and Responses

BustAPI uses `Request` and `Response` objects to handle HTTP traffic.

## The Request Object

You can access the global `request` object to handle incoming data.

```python
from bustapi import request
```

### Query Parameters

Access URL parameters (e.g., `?key=value`) using `request.args`.

```python
@app.route("/search")
def search():
    query = request.args.get("q")
    return f"Searching for: {query}"
```

### Form Data

Access form data from `POST` or `PUT` requests using `request.form`.

```python
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    return f"Logged in as {username}"
```

### JSON Data

For APIs, accessing JSON payload is common.

```python
@app.route("/api/data", methods=["POST"])
def api():
    data = request.get_json()
    return {"received": data}
```

### Headers and Cookies

```python
@app.route("/info")
def info():
    user_agent = request.headers.get("User-Agent")
    session_id = request.cookies.get("session_id")
    return {"ua": user_agent, "session": session_id}
```

---

## The Response Object

In most cases, returning a string or dict is enough. But for fine control, use the `Response` object or helper functions.

### JSON Responses

Returning a dict automatically creates a JSON response. You can also use `jsonify()` explicitly.

```python
from bustapi import jsonify

@app.route("/users")
def get_users():
    return jsonify([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
```

### Custom Headers and Status Code

You can return a tuple `(body, status, headers)`.

```python
@app.route("/teapot")
def teapot():
    return "I'm a teapot", 418, {"X-Custom": "HeaderValue"}
```

### Helper: `make_response`

```python
from bustapi import make_response

@app.route("/cookie")
def set_cookie():
    resp = make_response("Setting cookie")
    resp.set_cookie("username", "the_user")
    return resp
```

### Redirects and Errors

```python
from bustapi import redirect, abort

@app.route("/old")
def old_page():
    return redirect("/new")

@app.route("/hidden")
def hidden():
    abort(403, description="Access Forbidden")
```
