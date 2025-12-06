from flask import Flask, jsonify

app = Flask(__name__)


# 1. Plain Text
@app.route("/")
def index():
    return "Hello, World!"


# 2. JSON
@app.route("/json")
def json_endpoint():
    return jsonify({"message": "Hello, World!"})


# 3. Dynamic Path
@app.route("/user/<int:user_id>")
def user(user_id):
    return jsonify({"user_id": user_id, "name": f"User {user_id}"})
