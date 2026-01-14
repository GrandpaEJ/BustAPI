#!/usr/bin/env python3
"""Test script for typed turbo routes."""

from bustapi import BustAPI

app = BustAPI()


# Static turbo route (existing)
@app.turbo_route("/health")
def health():
    return {"status": "ok"}


# Typed turbo route with int param
@app.turbo_route("/users/<int:id>")
def get_user(id: int):
    return {"id": id, "name": f"User {id}"}


# Typed turbo route with multiple params
@app.turbo_route("/posts/<int:post_id>/comments/<int:comment_id>")
def get_comment(post_id: int, comment_id: int):
    return {"post_id": post_id, "comment_id": comment_id}


# Typed turbo route with string param
@app.turbo_route("/greet/<name>")
def greet(name: str):
    return {"message": f"Hello, {name}!"}


# Typed turbo route with float param
@app.turbo_route("/calc/<float:value>")
def double(value: float):
    return {"result": value * 2}


if __name__ == "__main__":
    print("Testing typed turbo routes...")
    print("Endpoints:")
    print("  GET /health")
    print("  GET /users/<int:id>")
    print("  GET /posts/<int:post_id>/comments/<int:comment_id>")
    print("  GET /greet/<name>")
    print("  GET /calc/<float:value>")
    print()
    app.run(port=5000, debug=False)
