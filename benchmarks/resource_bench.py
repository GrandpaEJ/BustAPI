#!/usr/bin/env python3
"""
BustAPI Resource Benchmark
Measures RPS, Latency, CPU%, and RAM Usage under load.
"""

import os
import signal
import subprocess
import threading
import time
import psutil
from bustapi import BustAPI

# Configuration
PORT = 8081
DURATION = "10s"
THREADS = 2
CONNECTIONS = 50  # Single core doesn't need as much concurrency


class ResourceMonitor:
    def __init__(self, pid):
        self.process = psutil.Process(pid)
        self.cpu_samples = []
        self.ram_samples = []
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.cpu_samples = []
        self.ram_samples = []
        self.thread = threading.Thread(target=self._monitor)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _monitor(self):
        # Initial CPU call
        try:
            self.process.cpu_percent()
        except:
            pass

        children_cache = {}

        while self.running:
            try:
                # Get main process stats
                cpu = self.process.cpu_percent()
                mem = self.process.memory_info().rss

                # Get children stats (workers)
                try:
                    children = self.process.children(recursive=True)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    children = []

                current_pids = {p.pid for p in children}

                # Track children
                for child in children:
                    if child.pid not in children_cache:
                        children_cache[child.pid] = child
                        try:
                            child.cpu_percent()  # init
                        except:
                            pass

                    try:
                        c = children_cache[child.pid]
                        if c.is_running():
                            cpu += c.cpu_percent()
                            mem += c.memory_info().rss
                    except:
                        pass

                self.cpu_samples.append(cpu)
                self.ram_samples.append(mem / 1024 / 1024)  # MB
                time.sleep(0.1)
            except:
                break

    def get_stats(self):
        if not self.cpu_samples:
            return 0.0, 0.0
        # Avg CPU over the duration
        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples)
        # Max RAM used
        max_ram = max(self.ram_samples) if self.ram_samples else 0.0
        return avg_cpu, max_ram


def create_server():
    # Write a temporary server file to ensure clean process start
    code = """
from bustapi import BustAPI
app = BustAPI()

@app.turbo_route("/json")
def json_endpoint():
    return {"hello": "world"}

@app.route("/user/<int:id>")
def user(id: int):
    return {"id": id}

@app.route("/api/v1/resource25/<int:id>")
def heavy_route(id: int):
    # Simulate slight work
    return {"id": id, "data": "x" * 100}

@app.route("/normal")
def normal_route():
    return {"status": "normal"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, workers=1, debug=False)
"""
    with open("bench_server.py", "w") as f:
        f.write(code)


def run_benchmark(endpoint, label):
    print(f"\n⚡ Benchmarking {label} ({endpoint})...")

    # Start server
    cmd = ["uv", "run", "python", "bench_server.py"]
    proc = subprocess.Popen(
        cmd, preexec_fn=os.setsid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(3)  # Warmup

    monitor = ResourceMonitor(proc.pid)
    monitor.start()

    # Run wrk
    wrk_cmd = [
        "wrk",
        "-t",
        str(THREADS),
        "-c",
        str(CONNECTIONS),
        "-d",
        DURATION,
        "--latency",
        f"http://127.0.0.1:{PORT}{endpoint}",
    ]

    result = subprocess.run(wrk_cmd, capture_output=True, text=True)
    monitor.stop()

    # Stats
    avg_cpu, max_ram = monitor.get_stats()

    # Parse wrk output
    output = result.stdout
    import re

    rps_match = re.search(r"Requests/sec:\s+([\d.]+)", output)
    rps = float(rps_match.group(1)) if rps_match else 0.0

    lat_match = re.search(
        r"Latency\s+([\d\.]+\w+)\s+([\d\.]+\w+)\s+([\d\.]+\w+)", output
    )
    avg_lat = lat_match.group(1) if lat_match else "N/A"

    print(f"   ➤ RPS: {rps:,.0f}")
    print(f"   ➤ Avg Latency: {avg_lat}")
    print(f"   ➤ CPU Usage: {avg_cpu:.1f}% (across 4 workers)")
    print(f"   ➤ RAM Usage: {max_ram:.1f} MB")

    # Cleanup
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    proc.wait()
    time.sleep(1)

    return {
        "Endpoint": label,
        "RPS": rps,
        "Latency": avg_lat,
        "CPU": f"{avg_cpu:.1f}%",
        "RAM": f"{max_ram:.1f} MB",
    }


if __name__ == "__main__":
    create_server()

    try:
        results = []
        results.append(run_benchmark("/json", "Static Turbo"))
        results.append(run_benchmark("/normal", "Normal Route"))
        results.append(run_benchmark("/user/123", "Dynamic Typed"))
        results.append(run_benchmark("/api/v1/resource25/999", "Deep Path"))

        print("\n" + "=" * 65)
        print(
            f"{'Endpoint':<20} | {'RPS':<10} | {'Latency':<10} | {'CPU %':<10} | {'RAM':<10}"
        )
        print("-" * 65)
        for r in results:
            print(
                f"{r['Endpoint']:<20} | {r['RPS']:<10,.0f} | {r['Latency']:<10} | {r['CPU']:<10} | {r['RAM']:<10}"
            )
        print("=" * 65)

    finally:
        if os.path.exists("bench_server.py"):
            os.remove("bench_server.py")
        subprocess.run(f"fuser -k {PORT}/tcp", shell=True, stderr=subprocess.DEVNULL)
