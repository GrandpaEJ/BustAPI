# Middleware & Hooks

You can hook into the request lifecycle to execute code before or after a request is processed.

## Request Hooks

### `before_request`

Runs before the route handler. Useful for validation or global setup.

```python
@app.before_request
def check_auth():
    if request.path.startswith("/admin") and not is_logged_in():
        return "Unauthorized", 401
```

If a `before_request` function returns a response, the request handling stops there, and that response is sent.

### `after_request`

Runs after the route handler. Useful for modifying the response (e.g., adding headers).

```python
@app.after_request
def add_header(response):
    response.headers["X-Powered-By"] = "BustAPI"
    return response
```

## Teardown

`teardown_request` runs at the very end of the request, even if an error occurred. Useful for cleaning up database connections.
