# Routing

BustAPI uses an intuitive routing system similar to Flask.

## Basic Routes

```python
@app.route("/")
def home(request):
    return "Hello World"
```

## Dynamic Routes

You can capture parts of the URL as arguments.

```python
@app.route("/user/<name>")
def user_profile(request, name):
    return f"User: {name}"

@app.route("/post/<int:post_id>")
def show_post(request, post_id: int):
    return {"id": post_id}
```

Supported converters:

- `<str:name>` (default)
- `<int:id>`
- `<float:value>`

## HTTP Methods

By default, routes only handle `GET` requests. You can specify other methods:

```python
@app.route("/login", methods=["GET", "POST"])
def login(request):
    if request.method == "POST":
        return "Logging in..."
    return "Login Page"
```
