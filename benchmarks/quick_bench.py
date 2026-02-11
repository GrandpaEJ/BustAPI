import os
import subprocess
import time
import signal
import re
import sys

CODE_BUSTAPI = """
from bustapi import BustAPI
app = BustAPI()

# Turbo routes - zero overhead
@app.turbo_route("/")
def index():
    return "Hello, World!"

@app.turbo_route("/json")
def json_endpoint():
    return {"hello": "world"}

@app.route("/user/<id>")
def user(id):
    return {"user_id": int(id)}
    
# Typed turbo route
@app.turbo_route("/typed/<int:id>")
def typed_user(id):
    return {"id": id}

@app.static_route("/static")
def static_endpoint():
    return "Static Content"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, workers=4, debug=False)
"""


def run_wrk(endpoint):
    result = subprocess.run(
        [
            "wrk",
            "-t4",
            "-c100",
            "-d3s",
            "--latency",
            f"http://127.0.0.1:8000{endpoint}",
        ],
        capture_output=True,
        text=True,
    )
    output = result.stdout
    rps_match = re.search(r"Requests/sec:\s+([\d.]+)", output)
    rps = float(rps_match.group(1)) if rps_match else 0
    print(f"{endpoint}: {rps:,.2f} req/sec")
    return rps


def main():
    print("🚀 Quick Bench BustAPI...")
    with open("temp_quick_bustapi.py", "w") as f:
        f.write(CODE_BUSTAPI)

    # Kill existing
    subprocess.run("fuser -k 8000/tcp", shell=True, stderr=subprocess.DEVNULL)
    time.sleep(1)

    proc = subprocess.Popen(
        ["python", "temp_quick_bustapi.py"],
        stdout=None,
        stderr=None,
    )
    time.sleep(3)

    try:
        run_wrk("/")
        run_wrk("/json")
        run_wrk("/typed/10")
        run_wrk("/static")
    finally:
        os.kill(proc.pid, signal.SIGTERM)
        time.sleep(1)
        if os.path.exists("temp_quick_bustapi.py"):
            os.remove("temp_quick_bustapi.py")


if __name__ == "__main__":
    main()
