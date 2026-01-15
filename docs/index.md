# BustAPI

<div align="center" markdown>

![BustAPI Logo](assets/logo.png){ width="180" }

**The fastest Python web framework.**  
*Flask-like API. Rust-powered performance. 100,000+ requests/sec.*

[:material-rocket-launch: Get Started](quickstart.md){ .md-button .md-button--primary }
[:material-github: GitHub](https://github.com/GrandpaEJ/BustAPI){ .md-button }

</div>

---

## :zap: Why BustAPI?

<div class="grid cards" markdown>

-   :material-speedometer:{ .lg .middle } **Blazing Fast**

    ---

    **100,000+ requests/sec** on Linux with multiprocessing.  
    Rust core with zero-copy optimizations.

-   :material-flask-outline:{ .lg .middle } **Flask-like API**

    ---

    Familiar decorators and patterns.  
    Switch from Flask in minutes, not days.

-   :material-language-python:{ .lg .middle } **Pure Python**

    ---

    Write normal Python code.  
    All the speed without the complexity.

-   :material-shield-check:{ .lg .middle } **Production Ready**

    ---

    JWT auth, sessions, validation.  
    Everything you need out of the box.

</div>

---

## :stopwatch: Quick Start

=== "Hello World"

    ```python
    from bustapi import BustAPI

    app = BustAPI()

    @app.route("/")
    def hello():
        return {"message": "Hello, World!"}

    if __name__ == "__main__":
        app.run()
    ```

=== "Turbo Route (~90k RPS)"

    ```python
    @app.turbo_route("/users/<int:id>")
    def get_user(id: int):
        return {"id": id, "name": f"User {id}"}
    ```

=== "Cached Route (~160k RPS)"

    ```python
    @app.turbo_route("/", cache_ttl=60)
    def home():
        return {"message": "Cached for 60 seconds!"}
    ```

=== "Multiprocessing"

    ```python
    if __name__ == "__main__":
        app.run(
            host="0.0.0.0",
            port=5000,
            workers=4  # 100k+ RPS on Linux!
        )
    ```

---

## :bar_chart: Performance

???+ success "Benchmark Results (Linux, 4 workers)"

    | Framework | Requests/sec | Avg Latency | Memory |
    |:----------|-------------:|------------:|-------:|
    | **BustAPI** | **105,012** | **1.00ms** | **105 MB** |
    | Sanic | 76,469 | 1.32ms | 243 MB |
    | BlackSheep | 41,176 | 2.48ms | 219 MB |
    | FastAPI | 12,723 | 7.95ms | 254 MB |
    | Flask | 7,806 | 12.69ms | 160 MB |

    *Tested with `wrk -t4 -c50 -d10s` on Python 3.13, Intel i5-8365U*

### Cross-Platform Support

| Platform | RPS | Mode |
|:---------|----:|:-----|
| :fontawesome-brands-linux: **Linux** | **105,012** | Multiprocessing (`SO_REUSEPORT`) |
| :fontawesome-brands-apple: macOS | 35,560 | Single-process |
| :fontawesome-brands-windows: Windows | 17,772 | Single-process |

!!! tip "Production Tip"
    Deploy on **Linux** for maximum performance with kernel-level load balancing.

---

## :package: Installation

```bash
pip install bustapi
```

**Requires:** Python 3.10 - 3.14

Pre-built wheels available for Linux, macOS, and Windows.

---

## :books: Learn More

<div class="grid cards" markdown>

-   [:material-book-open-variant: **Quickstart**](quickstart.md)

    Get your first app running in 5 minutes.

-   [:material-routes: **Routing Guide**](user-guide/routing.md)

    Dynamic paths, blueprints, and patterns.

-   [:material-lightning-bolt: **Turbo Routes**](user-guide/turbo-routes.md)

    Maximum performance for simple endpoints.

-   [:material-server: **Multiprocessing**](user-guide/multiprocessing.md)

    Scale to 100k+ RPS with worker processes.

-   [:material-shield-key: **JWT Auth**](user-guide/jwt.md)

    Secure your API with token authentication.

-   [:material-cached: **Caching**](user-guide/caching.md)

    140k RPS with built-in response caching.

</div>

---

## :heart: Open Source

BustAPI is **MIT licensed** and open source.

[:material-star: Star on GitHub](https://github.com/GrandpaEJ/BustAPI){ .md-button }
[:material-bug: Report a Bug](https://github.com/GrandpaEJ/BustAPI/issues){ .md-button }
