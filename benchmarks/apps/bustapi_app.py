from bustapi import BustAPI

app = BustAPI()


@app.get("/hello")
def hello():
    return {"message": "hello"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001)
