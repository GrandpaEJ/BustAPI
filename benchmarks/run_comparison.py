#!/usr/bin/env python3
import json
import os
import re
import signal
import subprocess
import sys
import time

# Configuration
DURATION = "15s"
THREADS = "4"
CONNECTIONS = "100"
WRK_CMD = ["wrk", "-t", THREADS, "-c", CONNECTIONS, "-d", DURATION]

SERVERS = [
    {
        "name": "Flask",
        "command": [sys.executable, "-m", "gunicorn", "--bind", "127.0.0.1:8000", "--workers", "4", "benchmarks.flask_server:app"],
        "port": 8000,
        "host": "127.0.0.1"
    },
    {
        "name": "FastAPI",
        "command": [sys.executable, "-m", "uvicorn", "benchmarks.fastapi_server:app", "--host", "127.0.0.1", "--port", "8001", "--workers", "4", "--log-level", "warning"],
        "port": 8001,
        "host": "127.0.0.1"
    },
    {
        "name": "BustAPI",
        "command": [sys.executable, "benchmarks/benchmark_server.py"],
        "port": 5090,
        "host": "127.0.0.1"
    }
]

ENDPOINTS = [
    {"path": "/", "name": "Plain Text"},
    {"path": "/json", "name": "JSON"},
    {"path": "/user/123", "name": "Dynamic Path"}
]

def wait_for_port(host, port, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            subprocess.check_call(
                ["curl", "-s", f"http://{host}:{port}/"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError:
            time.sleep(0.5)
    return False

def parse_wrk_output(output):
    rps = 0.0
    latency = "N/A"

    # Parse Requests/sec
    rps_match = re.search(r"Requests/sec:\s+([\d\.]+)", output)
    if rps_match:
        rps = float(rps_match.group(1))

    # Parse Latency (Avg)
    lat_match = re.search(r"Latency\s+([\d\.]+)(\w+)", output)
    if lat_match:
        latency = f"{lat_match.group(1)}{lat_match.group(2)}"

    return rps, latency

def run_benchmark():
    results = {}

    print(f"🚀 Starting Benchmark (Duration: {DURATION}, Threads: {THREADS}, Connections: {CONNECTIONS})")
    print("=" * 60)

    for server in SERVERS:
        name = server["name"]
        print(f"\nTesting {name}...")

        # Start server
        process = subprocess.Popen(server["command"], preexec_fn=os.setsid)

        try:
            # Wait for startup
            if not wait_for_port(server["host"], server["port"]):
                print(f"❌ Failed to start {name}")
                continue

            print(f"✅ {name} started on port {server['port']}")

            server_results = []

            for endpoint in ENDPOINTS:
                url = f"http://{server['host']}:{server['port']}{endpoint['path']}"
                print(f"   Running wrk on {endpoint['name']} ({url})...")

                cmd = WRK_CMD + [url]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode != 0:
                    print(f"   ❌ wrk failed: {result.stderr}")
                    continue

                rps, latency = parse_wrk_output(result.stdout)
                print(f"   👉 RPS: {rps:,.2f} | Latency: {latency}")

                server_results.append({
                    "endpoint": endpoint["name"],
                    "rps": rps,
                    "latency": latency
                })

            results[name] = server_results

        finally:
            # Kill server group
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.wait()
            print(f"🛑 {name} stopped")
            time.sleep(2) # Cooldown

    return results

def generate_markdown(results):
    md = "# 🚀 Web Framework Benchmark Results\n\n"
    md += f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    md += f"**Config:** {DURATION} duration, {THREADS} threads, {CONNECTIONS} connections\n\n"

    # Summary Table
    md += "## 📊 Summary (Requests/sec)\n\n"
    md += "| Endpoint | Flask | FastAPI | BustAPI |\n"
    md += "|----------|-------|---------|---------|\n"

    endpoints = [e["name"] for e in ENDPOINTS]

    for ep in endpoints:
        row = f"| **{ep}** |"
        for name in ["Flask", "FastAPI", "BustAPI"]:
            res = next((r for r in results.get(name, []) if r["endpoint"] == ep), None)
            if res:
                row += f" {res['rps']:,.2f} |"
            else:
                row += " N/A |"
        md += row + "\n"

    md += "\n## 🏆 Relative Performance (vs Flask)\n\n"

    # Calculate multipliers
    for ep in endpoints:
        flask_res = next((r for r in results.get("Flask", []) if r["endpoint"] == ep), None)
        if not flask_res or flask_res["rps"] == 0:
            continue

        md += f"### {ep}\n"
        base_rps = flask_res["rps"]

        for name in ["FastAPI", "BustAPI"]:
            res = next((r for r in results.get(name, []) if r["endpoint"] == ep), None)
            if res:
                multiplier = res["rps"] / base_rps
                md += f"- **{name}**: {multiplier:.1f}x faster ({res['rps']:,.2f} RPS)\n"
        md += "\n"

    return md

if __name__ == "__main__":
    results = run_benchmark()
    md_output = generate_markdown(results)

    with open("benchmarks/README.md", "w") as f:
        f.write(md_output)

    print("\n" + "=" * 60)
    print("💾 Results saved to benchmarks/README.md")
    print(md_output)
