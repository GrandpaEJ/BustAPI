#!/usr/bin/env python3
"""Quick BustAPI benchmark to show current performance"""

from bustapi import BustAPI

app = BustAPI()

@app.turbo_route("/")
def index():
    return "Hello, World!"

@app.turbo_route("/json")
def json_endpoint():
    return {"hello": "world"}

@app.route("/user/<int:id>")
def user(id: int):
    return {"user_id": id}

if __name__ == "__main__":
    print("Starting BustAPI benchmark server on http://127.0.0.1:8080")
    print("Run: wrk -t4 -c100 -d10s http://127.0.0.1:8080/json")
    app.run(host="127.0.0.1", port=8080, workers=4, debug=False)
