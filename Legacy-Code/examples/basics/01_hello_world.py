from bustapi import BustAPI

app = BustAPI()


@app.route("/")
def index():
    return {"message": "Hello, World!", "framework": "BustAPI"}


if __name__ == "__main__":
    print("Running hello world example on http://127.0.0.1:5000")
    app.run(debug=False, port=5000, workers=2)
