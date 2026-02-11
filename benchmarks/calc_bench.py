import os
import re
import signal
import subprocess
import time

CODE_CALC = """
from bustapi import BustAPI
app = BustAPI()

# Compiled Route (Expression Evaluator)
# Logic: price * 1.2 (Tax calculation)
@app.compiled_route("/tax/<float:price>")
def calculate_tax(price):
    return {"original": price, "taxed": price * 1.2, "currency": "USD"}

# Compiled Route (Complex Math)
# Logic: (a + b) * c
@app.compiled_route("/math/<int:a>/<int:b>/<int:c>")
def do_math(a, b, c):
    return {"result": (a + b) * c}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8002, workers=4, debug=False)
"""


def run_wrk(endpoint):
    result = subprocess.run(
        [
            "wrk",
            "-t4",
            "-c100",
            "-d3s",
            "--latency",
            f"http://127.0.0.1:8002{endpoint}",
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
    print("🚀 Benchmarking Computed Routes (Expression Evaluator)...")
    with open("temp_calc_bench.py", "w") as f:
        f.write(CODE_CALC)

    # Kill existing
    subprocess.run("fuser -k 8002/tcp", shell=True, stderr=subprocess.DEVNULL)
    time.sleep(1)

    proc = subprocess.Popen(["python", "temp_calc_bench.py"], stdout=None, stderr=None)
    time.sleep(3)

    try:
        print("\n--- Tax Calculation (price * 1.2) ---")
        run_wrk("/tax/100.0")

        print("\n--- Complex Math ((a+b)*c) ---")
        run_wrk("/math/10/20/30")
    finally:
        os.kill(proc.pid, signal.SIGTERM)
        time.sleep(1)
        if os.path.exists("temp_calc_bench.py"):
            os.remove("temp_calc_bench.py")


if __name__ == "__main__":
    main()
