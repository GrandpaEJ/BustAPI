import sys
import threading
import time

import requests
from bustapi import BustAPI

app = BustAPI()


@app.route("/")
def home():
    return {"message": "Hello form server"}


@app.route("/ping")
def ping():
    return "pong"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        server = sys.argv[1]
        print(f"Starting server with {server}...")
        try:
            app.run(port=8001, server=server, debug=True)
        except KeyboardInterrupt:
            print("Stopped.")
    else:
        print("Usage: python examples/test_modes.py [rust|uvicorn|gunicorn|hypercorn]")
