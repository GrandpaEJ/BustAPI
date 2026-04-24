# Routing

Routing is the mechanism of mapping a URL to a specific function in your code. BustAPI uses a high-performance Radix Tree implementation in Rust for this purpose.

## Basic Registration

Use the `@app.route()` decorator to register a view function.

```python
@app.route("/")
def index():
    return "Index Page"

@app.route("/hello")
def hello():
    return "Hello Page"
```

!!! note "Trailing Slashes"
    BustAPI uses strict path routing by default (`redirect_slashes=True`). If a user requests `/hello/` but you defined `/hello`, they will be automatically redirected to `/hello` (and vice-versa).
    
    You can disable this behavior when initializing the app:
    ```python
    app = BustAPI(redirect_slashes=False)
    ```

## Variable Rules

You can capture parts of the URL as variables. The variable part is marked with `<variable_name>`.

```python
@app.route("/user/<username>")
def show_user(username):
    # username is passed as a string
    return f"User: {username}"
```

### Type Converters

You can enforce types directly in the URL rule. If the type match fails, BustAPI returns a 404 automatically.

| Converter | Description |
| :--- | :--- |
| `<string:name>` | Accepts any text without slashes (default). |
| `<int:id>` | Accepts positive integers only. |
| `<float:val>` | Accepts positive floating point numbers. |
| `<path:name>` | Accepts the rest of the path, including slashes. |

```python
@app.route("/post/<int:post_id>")
def show_post(post_id):
    # post_id is now a python int, not a string!
    return f"Post ID: {post_id}"
```

## HTTP Methods

Web applications use different HTTP methods for different actions. By default, a route only answers to `GET`.

```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return do_the_login()
    else:
        return show_the_login_form()
```

### Shorthand Decorators

BustAPI provides shortcuts for common methods, which are often cleaner to read.

```python
@app.get("/items")
def get_items():
    return ["item1", "item2"]

@app.post("/items")
def create_item():
    return "Created"
```
