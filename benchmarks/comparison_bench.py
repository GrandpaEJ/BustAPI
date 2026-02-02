"""
BustAPI vs The World (FastAPI, Quart, Flask)
Automated WebSocket Benchmark & Plot Generator

Usage: uv run python comparison_bench.py

Requires:
  - oha
  - matplotlib
  - psutil
  - quart, flask-sock, fastapi, uvicorn
"""

import json
import os
import re
import signal
import subprocess
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
import psutil

# --- 1. Embedded Competitor Server Code ---
COMPETITOR_SERVER_CODE = r"""
import sys
import uvicorn
import asyncio

USAGE = "Usage: python competitor_ws.py [fastapi|quart|flask] [port]"

if len(sys.argv) < 3:
    print(USAGE)
    sys.exit(1)

framework = sys.argv[1]
port = int(sys.argv[2])

print(f"Starting {framework} server on port {port}...")

if framework == "fastapi":
    from fastapi import FastAPI, WebSocket
    app = FastAPI()
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    if __name__ == "__main__":
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

elif framework == "quart":
    import uvicorn
    from quart import Quart, websocket
    app = Quart(__name__)
    @app.websocket("/ws")
    async def ws():
        while True:
            data = await websocket.receive()
            await websocket.send(data)
    if __name__ == "__main__":
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

elif framework == "flask":
    from flask import Flask
    from flask_sock import Sock
    app = Flask(__name__)
    sock = Sock(app)
    @sock.route('/ws')
    def echo(ws):
        while True:
            data = ws.receive()
            ws.send(data)
    if __name__ == "__main__":
        app.run(host="127.0.0.1", port=port, threaded=True)
"""


def write_competitor_script():
    with open("competitor_ws_temp.py", "w") as f:
        f.write(COMPETITOR_SERVER_CODE)
    return "competitor_ws_temp.py"


def remove_competitor_script():
    if os.path.exists("competitor_ws_temp.py"):
        os.remove("competitor_ws_temp.py")


# --- 2. Measurement Logic ---
def get_server_cmd(framework, port):
    if framework == "bustapi":
        # Use simple bustapi app inline or existing script?
        # Using module based execution to be safe or existing script?
        # Let's assume bustapi is installed or in path.
        # But we need a server. We can reuse bustapi_bench.py if it exists!
        if os.path.exists("bustapi_bench.py"):
            return ["uv", "run", "python", "bustapi_bench.py", "server", str(port)]
        return ["uv", "run", "python", "ws_server.py", str(port)]
    else:
        return ["uv", "run", "python", "competitor_ws_temp.py", framework, str(port)]


def measure(framework, port):
    cmd = get_server_cmd(framework, port)
    print(f"[{framework}] Starting server: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        time.sleep(3)  # Warmup
        try:
            p = psutil.Process(proc.pid)
        except psutil.NoSuchProcess:
            return None

        url = f"http://127.0.0.1:{port}/ws"
        if framework == "bustapi":
            url = f"http://127.0.0.1:{port}/ws/turbo"

        oha_cmd = [
            "oha",
            "-z",
            "5s",
            "-c",
            "50",
            "-H",
            "Connection: Upgrade",
            "-H",
            "Upgrade: websocket",
            "-H",
            "Sec-WebSocket-Version: 13",
            "-H",
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==",
            url,
        ]

        oha_proc = subprocess.Popen(
            oha_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        cpu_readings = []
        mem_readings = []
        children_map = {}

        while oha_proc.poll() is None:
            try:
                cpu = p.cpu_percent(interval=0.1)
                mem = p.memory_info().rss / 1024 / 1024

                for child in p.children(recursive=True):
                    if child.pid not in children_map:
                        children_map[child.pid] = child
                        child.cpu_percent(interval=None)

                for pid, child in list(children_map.items()):
                    if not child.is_running():
                        del children_map[pid]
                        continue
                    try:
                        cpu += child.cpu_percent(interval=None)
                        mem += child.memory_info().rss / 1024 / 1024
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                cpu_readings.append(cpu)
                mem_readings.append(mem)

            except psutil.NoSuchProcess:
                break

        stdout, _ = oha_proc.communicate()
        rps_match = re.search(r"Requests/sec:\s+([\d\.]+)", stdout)
        rps = float(rps_match.group(1)) if rps_match else 0.0
        avg_cpu = sum(cpu_readings) / len(cpu_readings) if cpu_readings else 0
        peak_mem = max(mem_readings) if mem_readings else 0

        return {
            "framework": framework,
            "rps": rps,
            "cpu_avg": avg_cpu,
            "mem_peak_mb": peak_mem,
        }

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except:
            proc.kill()
        try:
            for child in psutil.Process(proc.pid).children(recursive=True):
                child.kill()
        except:
            pass


# --- 3. Plotting Logic ---
def plot_results(results):
    frameworks = []
    rps_data = []
    cpu_data = []
    ram_data = []

    # Sort by RPS desc
    results.sort(key=lambda x: x["rps"], reverse=True)

    for r in results:
        frameworks.append(r["framework"].capitalize())
        rps_data.append(r["rps"])
        cpu_data.append(r["cpu_avg"])
        ram_data.append(r["mem_peak_mb"])

    # Colors
    color_rps = "#2E7D32"
    color_ram = "#9C27B0"
    color_cpu = "#FF9800"

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

    # Plot 1: RPS
    y_pos = np.arange(len(frameworks))
    bars1 = ax1.barh(y_pos, rps_data, align="center", color=color_rps)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(frameworks, fontweight="bold")
    ax1.invert_yaxis()
    ax1.set_xlabel("Handshakes Per Second (Higher is Better)", fontsize=11)
    ax1.set_title("WebSocket Handshake Capacity", fontsize=14, fontweight="bold")
    ax1.grid(axis="x", linestyle="--", alpha=0.7)

    for bar in bars1:
        width = bar.get_width()
        ax1.text(
            width + 100,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width):,}",
            va="center",
            fontweight="bold",
            color="black",
        )

    # Plot 2: Resources
    height = 0.35
    bars_ram = ax2.barh(
        y_pos - height / 2, ram_data, height, label="RAM (MB)", color=color_ram
    )
    bars_cpu = ax2.barh(
        y_pos + height / 2, cpu_data, height, label="CPU (%)", color=color_cpu
    )

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(frameworks, fontweight="bold")
    ax2.invert_yaxis()
    ax2.set_xlabel("Resource Usage", fontsize=11)
    ax2.set_title("Resource Efficiency (RAM & CPU)", fontsize=14, fontweight="bold")
    ax2.legend()
    ax2.grid(axis="x", linestyle="--", alpha=0.3)

    for bar in bars_ram:
        width = bar.get_width()
        ax2.text(
            width + 2,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width)} MB",
            va="center",
            fontsize=9,
            color=color_ram,
        )

    for bar in bars_cpu:
        width = bar.get_width()
        ax2.text(
            width + 2,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width)}%",
            va="center",
            fontsize=9,
            color=color_cpu,
        )

    plt.tight_layout()
    plt.savefig("benchmarks/benchmark_comparison.png", dpi=300)
    print("Saved benchmark_comparison.png")


# --- 4. Main ---
if __name__ == "__main__":
    write_competitor_script()
    try:
        configs = [
            ("bustapi", 8030),
            ("quart", 8031),
            ("flask", 8032),
            ("fastapi", 8033),
        ]
        results = []
        for fw, port in configs:
            res = measure(fw, port)
            if res:
                results.append(res)
            print(f"Result: {res}")

        with open("benchmark_results.json", "w") as f:
            json.dump(results, f, indent=2)

        plot_results(results)
    finally:
        remove_competitor_script()
