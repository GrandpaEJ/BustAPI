# API Reference

## Class: BustAPI

The main application class. You usually create one instance of this per application.

```python
class BustAPI(import_name: str = None, static_folder: str = 'static', template_folder: str = 'templates')
```

### Constructor Arguments
- **import_name** (`str`): The name of the application package. Using `__name__` is standard.
- **static_folder** (`str`): The folder where static files are served from. Default: `'static'`.
- **template_folder** (`str`): The folder containing Jinja2 templates. Default: `'templates'`.

### Methods

#### `run(host='127.0.0.1', port=5000, debug=False)`
Starts the development server. This runs a single-process server suitable for development.
- **host**: The hostname to listen on. Set to `'0.0.0.0'` to make the server available externally.
- **port**: The port to listen on.
- **debug**: If `True`, enables hot-reloading and debug pages.

#### `route(rule, **options)`
A decorator to register a function as a view handler. See [Routing](../core_concepts/routing.md) for details.

#### `register_blueprint(blueprint, **options)`
Registers a blueprint with the application.
- **blueprint**: The `Blueprint` instance to register.
- **url_prefix** (optional): Prefix to prepend to all routes in the blueprint.

#### `before_request(f)`
Registers a function to run before each request.

#### `after_request(f)`
Registers a function to run after each request. Expected to return the response object.

---

## Context Proxies

BustAPI relies on context locals to make global variables like `request` thread-safe.

### `request`
The Request object for the current request.
- **method** (`str`): HTTP method (GET, POST, etc).
- **path** (`str`): The path of the request.
- **args** (`MultiDict`): Parsed query parameters.
- **form** (`MultiDict`): Parsed form data.
- **headers** (`Headers`): Incoming request headers.
- **get_json(force=False, silent=False)**: Parses body as JSON.

### `g`
A general purpose object for storing data during a single request context. Usage span is limited to one request.

```python
from bustapi import g

@app.before_request
def load_user():
    g.user = get_user()
```

### `session`
A dict-like object that stores data across requests using signed cookies. Requires `app.secret_key` to be set.

```python
from bustapi import session
session['username'] = 'admin'
```

---

## Utilities

BustAPI provides several helper functions.

### `jsonify(data)`
Creates a `Response` with the given data serialized to JSON.

### `abort(status_code, description=None)`
Raises an HTTP exception, stopping request processing immediately.

### `redirect(location, code=302)`
Returns a response redirecting the client to a new location.

### `render_template(template_name, **context)`
Renders a template from the templates folder with the given context.
