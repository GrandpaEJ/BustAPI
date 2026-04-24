from bustapi import BustAPI, request

app = BustAPI()


@app.route("/echo/json", methods=["POST"])
def echo_json():
    data = request.json
    return {"received": data, "content_type": request.headers.get("Content-Type")}


@app.route("/echo/form", methods=["POST"])
def echo_form():
    # Depending on impl, request.form might be available
    return {
        "form_data": (
            dict(request.form) if hasattr(request, "form") else "Not implemented"
        ),
        "content_type": request.headers.get("Content-Type"),
    }


if __name__ == "__main__":
    print("Running request data example on http://127.0.0.1:5003")
    app.run(port=5003)
