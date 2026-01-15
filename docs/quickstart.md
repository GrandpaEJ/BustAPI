# :rocket: Quickstart

Get your first BustAPI app running in **under 5 minutes**.

---

## :package: Installation

=== ":material-language-python: pip"

    ```bash
    pip install bustapi
    ```

=== ":material-package: uv (faster)"

    ```bash
    uv pip install bustapi
    ```

!!! info "Requirements"
    - Python 3.10 - 3.14
    - Pre-built wheels for Linux, macOS, and Windows

---

## :wave: Hello World

Create a file called `app.py`:

```python title="app.py" linenums="1" hl_lines="5 6 7"
from bustapi import BustAPI

app = BustAPI()

@app.route("/")
def hello():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run(debug=True)
```

Run it:

```bash
python app.py
```

Open [:material-open-in-new: http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

!!! success "You should see"
    ```json
    {"message": "Hello, World!"}
    ```

---

## :zap: Level Up: Turbo Routes

For **maximum performance**, use `@app.turbo_route()`:

=== "Static Route"

    ```python
    @app.turbo_route("/health")
    def health():
        return {"status": "ok"}
    ```
    
    **Performance:** ~34,000 requests/sec

=== "Dynamic Route"

    ```python
    @app.turbo_route("/users/<int:id>")
    def get_user(id: int):
        return {"id": id, "name": f"User {id}"}
    ```
    
    **Performance:** ~30,000 requests/sec

=== "Cached Route"

    ```python
    @app.turbo_route("/", cache_ttl=60)
    def home():
        return {"message": "Cached for 60 seconds!"}
    ```
    
    **Performance:** ~140,000 requests/sec :fire:

!!! warning "Note"
    Turbo routes skip middleware and sessions for speed. Use `@app.route()` if you need those features.

---

## :rocket: Production Mode

For maximum performance, use **multiprocessing**:

```python title="app.py" linenums="1" hl_lines="6"
from bustapi import BustAPI

app = BustAPI()

# ... your routes ...

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        workers=4,      # (1)!
        debug=False     # (2)!
    )
```

1. :material-server: Spawns 4 worker processes for parallel request handling
2. :material-bug-outline: Always disable debug in production!

!!! tip "Linux Magic"
    On Linux, BustAPI uses `SO_REUSEPORT` for kernel-level load balancing.
    This achieves **100,000+ requests/sec** with 4 workers!

---

## :books: Next Steps

<div class="grid cards" markdown>

-   [:material-routes: **Routing Guide**](user-guide/routing.md)

    Learn about dynamic paths and blueprints.

-   [:material-lightning-bolt: **Turbo Routes**](user-guide/turbo-routes.md)

    Deep dive into high-performance routes.

-   [:material-server: **Multiprocessing**](user-guide/multiprocessing.md)

    Scale to 100k+ RPS on Linux.

-   [:material-shield-key: **JWT Auth**](user-guide/jwt.md)

    Secure your API with tokens.

</div>
