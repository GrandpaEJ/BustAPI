# Quickstart

Get started with BustAPI in under 5 minutes.

## Installation

```bash
pip install bustapi
```

**Requirements:** Python 3.10 - 3.14

## Your First App

Create `app.py`:

```python
from bustapi import BustAPI

app = BustAPI()

@app.route("/")
def hello():
    return {"message": "Hello, World!"}

@app.route("/users/<int:user_id>")
def get_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}

if __name__ == "__main__":
    app.run(debug=True)
```

Run it:

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## Turbo Routes (Maximum Speed)

For the highest performance, use `@app.turbo_route()`:

```python
from bustapi import BustAPI

app = BustAPI()

# 30,000+ requests/sec
@app.turbo_route("/health")
def health():
    return {"status": "ok"}

# With typed path parameters
@app.turbo_route("/users/<int:id>")
def get_user(id: int):
    return {"id": id}

# With caching (140,000+ requests/sec!)
@app.turbo_route("/cached", cache_ttl=60)
def cached():
    return {"data": "This response is cached for 60 seconds"}

if __name__ == "__main__":
    app.run(workers=4)  # Use 4 worker processes
```

> ⚡ **Turbo routes** skip middleware and sessions for speed. Use `@app.route()` if you need those features.

---

## Production Deployment

For maximum performance on Linux:

```python
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        workers=4,      # Use 4 worker processes
        debug=False     # Disable debug in production
    )
```

This achieves **100,000+ requests/sec** on Linux with `SO_REUSEPORT` load balancing.

## Next Steps

- [Routing Guide](user-guide/routing.md)
- [Turbo Routes](user-guide/turbo-routes.md)
- [Multiprocessing](user-guide/multiprocessing.md)
- [JWT Authentication](user-guide/jwt.md)
