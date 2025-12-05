from bustapi import BustAPI

app = BustAPI()

# 1. Plain Text (using fast route for max performance comparison, or standard?)
# Let's use standard Python handlers to test the Python-Rust bridge performance,
# as that's what we are optimizing with Actix/PyO3.
# Fast routes are Rust-only and would obviously win.

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/json")
def json_endpoint():
    return {"message": "Hello, World!"}

@app.route("/user/<id>")
def user(id):
    return {"user_id": int(id), "name": f"User {id}"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5090)
