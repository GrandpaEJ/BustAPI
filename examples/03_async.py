import asyncio

from bustapi import BustAPI

app = BustAPI()


@app.route("/sync")
def sync_handler():
    return {"mode": "sync"}


@app.route("/async")
async def async_handler():
    # Simulate async work
    await asyncio.sleep(0.1)
    return {"mode": "async", "waited": 0.1}


if __name__ == "__main__":
    print("Running async example on http://127.0.0.1:5002")
    app.run(port=5002)
