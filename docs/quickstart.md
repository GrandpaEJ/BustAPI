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

=== "Dynamic Route"

    ```python
    @app.turbo_route("/users/<int:id>")
    def get_user(id: int):
        return {"id": id, "name": f"User {id}"}
    ```

=== "Cached Route"

    ```python
    @app.turbo_route("/", cache_ttl=60)
    def home():
        return {"message": "Cached for 60 seconds!"}
    ```

### Benchmark Results (v0.8.0)

Tested with `oha -z 10s -c 50` on Python 3.13:

| Route Type | Linux (4w) | macOS | Windows |
|:-----------|----------:|------:|--------:|
| Static turbo | 105,012 | 35,560 | 17,772 |
| Dynamic turbo | 99,142 | 27,532 | 17,844 |
| Cached turbo | ~160,000 | - | - |

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

### Platform Performance (v0.8.0)

| Platform | Workers | RPS | Note |
|:---------|--------:|----:|:-----|
| :fontawesome-brands-linux: Linux | 4 | **105,012** | `SO_REUSEPORT` load balancing |
| :fontawesome-brands-apple: macOS | 1 | 35,560 | Single-process mode |
| :fontawesome-brands-windows: Windows | 1 | 17,772 | Single-process mode |

!!! tip "Production Recommendation"
    Deploy on **Linux** for maximum performance with kernel-level load balancing.

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
