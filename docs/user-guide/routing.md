# Routing

Modern web applications use meaningful URLs to help users. BustAPI provides a decorator-based routing system similar to Flask.

## Basic Routing

Use the `route()` decorator to bind a function to a URL.

```python
@app.route("/")
def index():
    return "Index Page"

@app.route("/hello")
def hello():
    return "Hello, World"
```

## Variable Rules

You can add variable sections to a URL by marking sections with `<variable_name>`. The value is passed as a keyword argument to your function.

```python
@app.route("/user/<username>")
def show_user_profile(username):
    # show the user profile for that user
    return f"User {username}"

@app.route("/post/<int:post_id>")
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return f"Post {post_id}"
```

### Supported Converters

- **`string`**: (Default) Accepts any text without a slash.
- **`int`**: Accepts positive integers.
- **`path`**: Accepts text strings including slashes (useful for file paths).

## HTTP Methods

By default, a route only answers to `GET` requests. You can use the `methods` argument to handle different HTTP methods.

```python
from bustapi import request

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return do_the_login()
    else:
        return show_the_login_form()
```

## URL Building

You can build a URL to a specific function using `url_for()`. This is safer than hardcoding URLs.

```python
from bustapi import url_for

with app.test_request_context():
    print(url_for("index"))  # Output: /
    print(url_for("login"))  # Output: /login
    print(url_for("show_user_profile", username="Grandpa")) # Output: /user/Grandpa
```
