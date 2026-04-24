# Error Handling

Applications fail. BustAPI allows you to handle these failures gracefully.

## Handling HTTP Errors

You can use the `errorhandler` decorator to catch specific HTTP status codes.

```python
from bustapi import render_template

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
```

## Handling Exceptions

You can also handle generic Python exceptions.

```python
@app.errorhandler(ValueError)
def handle_value_error(e):
    return {"error": "Invalid value provided", "details": str(e)}, 400
```

## Raising Errors

You can stop request processing and return an error manually using `abort()`.

```python
from bustapi import abort

@app.route("/admin")
def admin():
    if not is_admin():
        abort(403, description="Admins only!")
    return "Welcome Admin"
```
