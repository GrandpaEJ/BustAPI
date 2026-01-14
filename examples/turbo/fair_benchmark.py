#!/usr/bin/env python3
"""Fair benchmark comparison: Static, Dynamic, and Cached turbo routes."""

from bustapi import BustAPI

app = BustAPI()


# 1. Static turbo (no cache, no params)
@app.turbo_route("/static")
def static_endpoint():
    return {"status": "ok"}


# 2. Dynamic turbo (no cache, with params)
@app.turbo_route("/dynamic/<int:id>")
def dynamic_endpoint(id: int):
    return {"id": id}


# 3. Cached static (10s TTL)
@app.turbo_route("/cached", cache_ttl=10)
def cached_endpoint():
    return {"cached": True}


# 4. Cached dynamic (10s TTL)
@app.turbo_route("/cached/<int:id>", cache_ttl=10)
def cached_dynamic(id: int):
    return {"id": id, "cached": True}


if __name__ == "__main__":
    print("Fair Benchmark Comparison")
    print("=" * 40)
    print("  GET /static       - Static turbo (no cache)")
    print("  GET /dynamic/42   - Dynamic turbo (no cache)")
    print("  GET /cached       - Static cached (10s TTL)")
    print("  GET /cached/42    - Dynamic cached (10s TTL)")
    print()
    app.run(port=5000, debug=False)
