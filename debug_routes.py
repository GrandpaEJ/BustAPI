# ruff: noqa: B008
#!/usr/bin/env python3
"""Quick test to debug route registration."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "python"))

from bustapi import Body, BustAPI

app = BustAPI()


@app.route("/test", methods=["POST"])
def test_body(user: dict = Body(..., schema={"name": {"type": "str"}})):
    print(f"DEBUG: user type = {type(user)}")
    print(f"DEBUG: user value = {user}")
    return {"user": user}


# Check registered routes
print(f"View functions: {app.view_functions}")
print(f"URL map: {app.url_map}")

# Try calling the view function directly
print("\nCalling view function directly:")
try:
    result = app.view_functions["test_body"]()
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
