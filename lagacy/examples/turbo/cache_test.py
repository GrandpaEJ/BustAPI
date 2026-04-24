#!/usr/bin/env python3
"""Test script for response caching in turbo routes."""

import time

from bustapi import BustAPI

app = BustAPI()

call_count = {"cached": 0, "uncached": 0}


# Cached route - 10 second TTL
@app.turbo_route("/cached", cache_ttl=10)
def cached_endpoint():
    call_count["cached"] += 1
    return {"call_count": call_count["cached"], "time": time.time()}


# Uncached route
@app.turbo_route("/uncached")
def uncached_endpoint():
    call_count["uncached"] += 1
    return {"call_count": call_count["uncached"], "time": time.time()}


# Cached dynamic route
@app.turbo_route("/users/<int:id>", cache_ttl=5)
def get_user(id: int):
    return {"id": id, "fetched_at": time.time()}


if __name__ == "__main__":
    print("Testing response caching...")
    print("Endpoints:")
    print("  GET /cached (10s cache)")
    print("  GET /uncached (no cache)")
    print("  GET /users/<int:id> (5s cache)")
    print()
    app.run(port=5000, debug=False)
