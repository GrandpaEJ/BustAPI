from bustapi import BustAPI, jsonify

app = BustAPI()


@app.route("/user/<int:user_id>/profile")
def user_profile(user_id):
    """Match exact structure with int converter."""
    return jsonify(
        {
            "route": "/user/<int:user_id>/profile",
            "user_id": user_id,
            "type": str(type(user_id)),
        }
    )


@app.route("/files/<path>/<filename>")
def file_info(path, filename):
    """Match multiple string segments."""
    return jsonify(
        {"route": "/files/<path>/<filename>", "path": path, "filename": filename}
    )


@app.route("/api/<version>/products/<int:product_id>")
def product_detail(version, product_id):
    """Mixed types and multiple segments."""
    return jsonify(
        {"api_version": version, "product_id": product_id, "status": "available"}
    )


if __name__ == "__main__":
    print("Running complex routing example on http://127.0.0.1:5008")
    app.run(port=5008, debug=True)
