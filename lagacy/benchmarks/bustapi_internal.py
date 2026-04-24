#!/usr/bin/env python3
"""
BustAPI Internal Benchmark: Normal Routes vs Turbo Routes

Compares performance between:
- @app.route() - Full featured routes (middleware, context, sessions)
- @app.turbo_route() - Ultra-fast routes (no overhead)

Usage:
    python benchmarks/bustapi_internal.py
"""

import os
import signal
import subprocess
import sys
import time

# ===================== CONFIG =====================
WORKERS = 1  # Number of server workers
DURATION = 5  # Benchmark duration in seconds
THREADS = 4  # wrk threads
CONNECTIONS = 100  # concurrent connections
PORT = 8000  # Server port
# =================================================


# Benchmark server code - uses f-string to inject config
def get_server_code():
    return f"""\nimport random
import time
from bustapi import BustAPI

app = BustAPI()

# ================= NORMAL ROUTES =================

@app.route("/")
def normal_root():
    return {{"message": "Hello from normal route"}}

@app.route("/json")
def normal_json():
    return {{"data": [1, 2, 3, 4, 5], "status": "ok"}}

@app.route("/user/<int:id>")
def normal_user(id):
    return {{"id": id, "name": "User", "type": "normal"}}

# Dynamic - generates new data each time
@app.route("/dynamic")
def normal_dynamic():
    return {{
        "timestamp": time.time(),
        "random_id": random.randint(1, 1000000),
        "data": [random.random() for _ in range(10)],
        "status": "fresh"
    }}

# ================= TURBO ROUTES =================

@app.turbo_route("/turbo")
def turbo_root():
    return {{"message": "Hello from turbo route"}}

@app.turbo_route("/turbo/json")
def turbo_json():
    return {{"data": [1, 2, 3, 4, 5], "status": "ok"}}

@app.turbo_route("/turbo/user/<int:id>")
def turbo_user(id: int):
    return {{"id": id, "name": "User", "type": "turbo"}}

# Dynamic turbo - generates new data each time
@app.turbo_route("/turbo/dynamic")
def turbo_dynamic():
    return {{
        "timestamp": time.time(),
        "random_id": random.randint(1, 1000000),
        "data": [random.random() for _ in range(10)],
        "status": "fresh"
    }}

# ================= CACHED TURBO =================

@app.turbo_route("/cached", cache_ttl=60)
def cached_route():
    return {{"cached": True, "data": "This is cached for 60 seconds"}}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port={PORT}, workers={WORKERS})
"""


def run_wrk(url: str, duration: int = 10, threads: int = 4, connections: int = 100):
    """Run wrk benchmark and return results."""
    cmd = f"wrk -t{threads} -c{connections} -d{duration}s --latency {url}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return parse_wrk_output(result.stdout)
    except Exception as e:
        return {"error": str(e)}


def parse_wrk_output(output: str) -> dict:
    """Parse wrk output to extract metrics."""
    import re

    result = {"rps": 0, "avg_latency": "N/A", "max_latency": "N/A", "transfer": "N/A"}

    # Extract RPS
    rps_match = re.search(r"Requests/sec:\s+([\d.]+)", output)
    if rps_match:
        result["rps"] = float(rps_match.group(1))

    # Extract Latency
    latency_match = re.search(r"Latency\s+([\d.]+\w+)", output)
    if latency_match:
        result["avg_latency"] = latency_match.group(1)

    # Max latency
    max_lat = re.search(r"Latency.*?Max\s+([\d.]+\w+)", output, re.DOTALL)
    if max_lat:
        result["max_latency"] = max_lat.group(1)

    # Transfer
    transfer_match = re.search(r"Transfer/sec:\s+([\d.]+\w+)", output)
    if transfer_match:
        result["transfer"] = transfer_match.group(1)

    return result


def wait_for_server(url: str, timeout: int = 10):
    """Wait for server to be ready."""
    import urllib.request

    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except:
            time.sleep(0.2)
    return False


def main():
    print("\n" + "=" * 60)
    print("🚀 BustAPI Internal Benchmark: Normal vs Turbo Routes")
    print("=" * 60)

    # Create temp server file
    server_file = "benchmarks/_temp_internal_server.py"
    with open(server_file, "w") as f:
        f.write(get_server_code())

    # Kill any existing process on port
    subprocess.run(f"fuser -k {PORT}/tcp 2>/dev/null", shell=True)
    time.sleep(0.5)

    # Start server
    print("\n📡 Starting BustAPI server...")
    server_proc = subprocess.Popen(
        [sys.executable, server_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        if not wait_for_server(f"http://127.0.0.1:{PORT}/"):
            print("❌ Server failed to start!")
            return

        print(f"✅ Server ready! (workers={WORKERS}, port={PORT})\n")
        print(
            f"📋 Config: duration={DURATION}s, threads={THREADS}, connections={CONNECTIONS}\n"
        )

        # Define endpoints to test
        base = f"http://127.0.0.1:{PORT}"
        endpoints = [
            ("Normal: /", f"{base}/"),
            ("Turbo: /turbo", f"{base}/turbo"),
            ("Normal: /json", f"{base}/json"),
            ("Turbo: /turbo/json", f"{base}/turbo/json"),
            ("Normal: /user/10", f"{base}/user/10"),
            ("Turbo: /turbo/user/10", f"{base}/turbo/user/10"),
            ("Normal: /dynamic", f"{base}/dynamic"),
            ("Turbo: /turbo/dynamic", f"{base}/turbo/dynamic"),
            ("Cached: /cached", f"{base}/cached"),
        ]

        results = []

        for name, url in endpoints:
            print(f"⏱️  Benchmarking {name}...")
            res = run_wrk(
                url, duration=DURATION, threads=THREADS, connections=CONNECTIONS
            )
            results.append((name, res))
            print(f"   → {res['rps']:,.0f} req/sec | Latency: {res['avg_latency']}")

        # Print comparison table
        print("\n" + "=" * 60)
        print("📊 RESULTS COMPARISON")
        print("=" * 60)
        print(f"{'Endpoint':<25} {'RPS':>12} {'Latency':>12} {'Speedup':>10}")
        print("-" * 60)

        # Group by pairs for comparison (normal, turbo)
        pairs = [
            (results[0], results[1]),  # root
            (results[2], results[3]),  # json
            (results[4], results[5]),  # user
            (results[6], results[7]),  # dynamic
        ]

        for (normal_name, normal_res), (turbo_name, turbo_res) in pairs:
            # Normal
            print(
                f"{normal_name:<25} {normal_res['rps']:>12,.0f} {normal_res['avg_latency']:>12}"
            )

            # Turbo with speedup
            speedup = (
                turbo_res["rps"] / normal_res["rps"] if normal_res["rps"] > 0 else 0
            )
            print(
                f"{turbo_name:<25} {turbo_res['rps']:>12,.0f} {turbo_res['avg_latency']:>12} {speedup:>9.2f}x"
            )
            print()

        # Cached route (last item)
        cached = results[-1]
        print(
            f"{'Cached: /cached':<25} {cached[1]['rps']:>12,.0f} {cached[1]['avg_latency']:>12}"
        )

        print("-" * 60)

        # Summary - include all normal vs turbo pairs
        normal_avg = sum(results[i][1]["rps"] for i in range(0, 8, 2)) / 4
        turbo_avg = sum(results[i][1]["rps"] for i in range(1, 8, 2)) / 4

        print(f"\n📈 Average Normal Route:  {normal_avg:>12,.0f} req/sec")
        print(f"📈 Average Turbo Route:   {turbo_avg:>12,.0f} req/sec")
        print(f"⚡ Turbo Speedup:         {turbo_avg / normal_avg:>12.2f}x faster")

    finally:
        # Cleanup
        server_proc.terminate()
        server_proc.wait()
        if os.path.exists(server_file):
            os.remove(server_file)
        print("\n🧹 Cleanup complete!")


if __name__ == "__main__":
    main()
