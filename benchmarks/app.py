import bustapi
print(f"DEBUG APP: bustapi imported from {bustapi.__file__}")
from bustapi import BustAPI, jsonify
app = BustAPI()

# Use turbo_route for maximum performance
@app.turbo_route("/")
def index():
    return "Hello, World!"

@app.turbo_route("/json")
def json_endpoint():
    return {"hello": "world"}

# Keep regular route for path params (turbo doesn't support params)
@app.route("/user/<id>")
def user(id):
    return jsonify({"user_id": int(id)})

@app.turbo_route("/large")
def large():
    return {"data": "x" * 2048}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, workers=8, debug=False)