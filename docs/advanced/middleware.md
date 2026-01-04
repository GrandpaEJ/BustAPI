# Middleware

Middleware allows you to hook into the request-response lifecycle. You can inspect requests before they reach your code, or modify responses before they are sent to the client.

## Request Hooks

The simplest way to implement middleware-like logic is using the `before_request` and `after_request` decorators.

### @app.before_request

Runs before the view function. If it returns a value, the request handling stops there and that value is used as the response.

```python
from bustapi import request, abort

@app.before_request
def check_api_key():
    if request.path.startswith("/api/"):
        key = request.headers.get("X-API-Key")
        if not key:
            abort(401)
```

### @app.after_request

Runs after the view function. It receives the response object, must modify it, and return it.

```python
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
```

## WSGI Middleware

Because BustAPI is WSGI compatible, you can wrapping the `app.wsgi_app` with any standard WSGI middleware.

```python
from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
```
