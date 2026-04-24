"""
Example 14: Middleware
====================

This example demonstrates how to use `before_request` and `after_request` hooks
to implement simple middleware logic like logging, timing, or authentication.
"""

import time

from bustapi import BustAPI, abort, request

app = BustAPI()

# Global state to track request count
request_count = 0


@app.before_request
def start_timer():
    """Run before every request."""
    global request_count
    request_count += 1

    # Store start time on request object
    request.start_time = time.time()
    print(f"[{request.method}] {request.path} - Processing...")


@app.before_request
def check_auth():
    """Simulate authentication check."""
    # Example: Block access to /admin unless header is present
    if request.path.startswith("/admin"):
        auth = request.headers.get("Authorization")
        if auth != "secret-token":
            return abort(401)


@app.after_request
def log_response(response):
    """Run after every request."""
    # Calculate duration
    if hasattr(request, "start_time"):
        duration = time.time() - request.start_time
        print(f"[{request.method}] {request.path} - Done in {duration:.4f}s")

    # Add custom header
    response.headers["X-Request-Count"] = str(request_count)
    return response


@app.route("/")
def home():
    return {"message": "Middleware Demo", "count": request_count}


@app.route("/admin/dashboard")
def admin():
    return {"message": "Welcome Admin!"}


@app.route("/slow")
def slow():
    time.sleep(1)
    return {"message": "That took a while"}


if __name__ == "__main__":
    app.run(debug=True)
