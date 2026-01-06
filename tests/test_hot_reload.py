import sys
import time

from bustapi import BustAPI

# Flush stdout immediately
sys.stdout.reconfigure(line_buffering=True)

app = BustAPI()


@app.route("/")
def index():
    return "Hot Reload Test"


if __name__ == "__main__":
    print("🚀 Starting with debug=True to test Rust hot-reloader...")
    # debug=True should trigger serving.py to call rust's enable_hot_reload
    app.run(debug=True, port=8001)
