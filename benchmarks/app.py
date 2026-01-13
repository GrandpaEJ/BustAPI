from bustapi import BustAPI, jsonify
app = BustAPI()

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/json")
def json_endpoint():
    return jsonify({"hello": "world"})

@app.route("/user/<id>")
def user(id):
    return jsonify({"user_id": int(id)})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, workers=4, debug=False)