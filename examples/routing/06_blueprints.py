from bustapi import Blueprint, BustAPI, jsonify

app = BustAPI()

# Create a Blueprint for API v1
api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")


@api_v1.route("/status")
def status():
    return jsonify({"status": "ok", "version": 1})


@api_v1.route("/users")
def users():
    return jsonify(["alice", "bob"])


# Create another Blueprint for Admin area
admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/dashboard")
def dashboard():
    return "<h1>Admin Dashboard</h1>"


# Register Blueprints
app.register_blueprint(api_v1)
app.register_blueprint(admin)


@app.route("/")
def home():
    return """
    <h1>Blueprints Example</h1>
    <ul>
        <li><a href="/api/v1/status">API Status</a></li>
        <li><a href="/api/v1/users">API Users</a></li>
        <li><a href="/admin/dashboard">Admin Dashboard</a></li>
    </ul>
    """


if __name__ == "__main__":
    print("Running blueprints example on http://127.0.0.1:5005")
    app.run(port=5005, debug=True)
