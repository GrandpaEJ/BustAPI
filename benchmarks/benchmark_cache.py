import multiprocessing
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

# Configuration
HOST = "127.0.0.1"
PORT = 8000
WRK_DURATION = "10s"  # Longer duration for stable cache stats
WRK_CONNECTIONS = 100
WRK_THREADS = 12
WORKERS = 4

SERVER_FILES = {
    "NoCache": "benchmarks/temp_no_cache.py",
    "Cached": "benchmarks/temp_cached.py",
}

RUN_COMMANDS = {
    "NoCache": ["python", "benchmarks/temp_no_cache.py"],
    "Cached": ["python", "benchmarks/temp_cached.py"],
}

CODE_NO_CACHE = f"""
from bustapi import BustAPI
import multiprocessing

app = BustAPI()

# Standard Turbo Route (No Cache)
@app.turbo_route("/")
def index():
    return "Hello, World!"

@app.turbo_route("/json")
def json_endpoint():
    return {{"hello": "world"}}

@app.turbo_route("/user/<int:id>")
def user(id: int):
    return {{"user_id": id}}

if __name__ == "__main__":
    app.run(host="{HOST}", port={PORT}, workers={WORKERS}, debug=False)
"""

CODE_CACHED = f"""
from bustapi import BustAPI
import multiprocessing

app = BustAPI()

# Cached Turbo Route (TTL=60s)
@app.turbo_route("/", cache_ttl=60)
def index():
    return "Hello, World!"

@app.turbo_route("/json", cache_ttl=60)
def json_endpoint():
    return {{"hello": "world"}}

@app.turbo_route("/user/<int:id>", cache_ttl=60)
def user(id: int):
    return {{"user_id": id}}

if __name__ == "__main__":
    app.run(host="{HOST}", port={PORT}, workers={WORKERS}, debug=False)
"""


@dataclass
class BenchmarkResult:
    name: str
    endpoint: str
    rps: float
    avg_latency_ms: float


def create_server_files():
    print("📝 Creating temporary server files...")
    with open(SERVER_FILES["NoCache"], "w") as f:
        f.write(CODE_NO_CACHE)
    with open(SERVER_FILES["Cached"], "w") as f:
        f.write(CODE_CACHED)


def clean_up():
    print("🧹 Cleaning up...")
    for f in SERVER_FILES.values():
        if os.path.exists(f):
            os.remove(f)
    subprocess.run(f"fuser -k {PORT}/tcp", shell=True, stderr=subprocess.DEVNULL)


def run_wrk(endpoint: str) -> dict:
    url = f"http://{HOST}:{PORT}{endpoint}"
    cmd = [
        "wrk",
        "-t",
        str(WRK_THREADS),
        "-c",
        str(WRK_CONNECTIONS),
        "-d",
        WRK_DURATION,
        "--latency",
        url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout

    data = {"rps": 0.0, "latency": 0.0}

    rps_match = re.search(r"Requests/sec:\s+([\d.]+)", output)
    if rps_match:
        data["rps"] = float(rps_match.group(1))

    latency_match = re.search(r"Latency\s+([\d\.]+)ms", output)
    if latency_match:
        data["latency"] = float(latency_match.group(1))

    return data


def benchmark_variant(name: str):
    print(f"\n🚀 Benchmarking {name}...")

    # Kill any existing on port
    subprocess.run(f"fuser -k {PORT}/tcp", shell=True, stderr=subprocess.DEVNULL)
    time.sleep(1)

    # Start Server
    cmd = RUN_COMMANDS[name]
    print(f"   Starting: {' '.join(cmd)}")

    proc = subprocess.Popen(
        cmd,
        cwd=os.getcwd(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid,
    )

    time.sleep(3)  # Warmup

    results = []
    endpoints = ["/", "/json", "/user/10"]

    try:
        for ep in endpoints:
            print(f"   Measuring {ep}...", end="", flush=True)
            res = run_wrk(ep)
            print(f" {res['rps']:.2f} req/sec, Latency: {res['latency']:.2f}ms")
            results.append(BenchmarkResult(name, ep, res["rps"], res["latency"]))
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=2)
        except:
            pass

    return results


def main():
    if not shutil.which("wrk"):
        print("❌ Error: 'wrk' tool number be installed.")
        return

    create_server_files()

    try:
        results_no_cache = benchmark_variant("NoCache")
        results_cached = benchmark_variant("Cached")

        # Generator Report
        report = "# ⚡ Cache vs No-Cache Benchmark\n\n"
        report += "| Endpoint | Variant | RPS | Avg Latency |\n"
        report += "| :--- | :--- | :---: | :---: |\n"

        for nc, c in zip(results_no_cache, results_cached):
            report += f"| **{nc.endpoint}** | No Cache | {nc.rps:,.0f} | {nc.avg_latency_ms:.2f}ms |\n"
            report += (
                f"| | ⚡ Cached | **{c.rps:,.0f}** | **{c.avg_latency_ms:.2f}ms** |\n"
            )
            improvement = ((c.rps - nc.rps) / nc.rps) * 100
            report += f"| | *Improvement* | *+{improvement:.1f}%* | |\n"
            report += "| | | | |\n"

        with open("benchmarks/CACHE_BENCHMARK.md", "w") as f:
            f.write(report)

        print("\n✅ Benchmark complete! Report saved to benchmarks/CACHE_BENCHMARK.md")
        print(report)

    finally:
        clean_up()


if __name__ == "__main__":
    main()
