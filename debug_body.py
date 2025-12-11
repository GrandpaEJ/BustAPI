# ruff: noqa: B008
#!/usr/bin/env python3
"""Quick test to debug Body validation."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "python"))

from bustapi import Body, BustAPI

app = BustAPI()


@app.route("/test", methods=["POST"])
def test_body(user: dict = Body(..., schema={"name": {"type": "str"}})):
    return {"user": user}


if __name__ == "__main__":
    from bustapi import TestClient

    client = TestClient(app)

    # Test valid request
    response = client.post("/test", json={"name": "Alice"})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code == 200:
        print(f"JSON: {response.json}")
