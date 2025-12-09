
#!/usr/bin/env python3
"""
Automated Framework Comparison Benchmark
BustAPI vs Flask vs FastAPI vs Catzilla

Requires: wrk, uv
"""

import os
import sys
import time
import json
import signal
import shutil
import subprocess
import threading
import psutil
from dataclasses import dataclass
from typing import Dict, List, Optional

# Configuration
PORT = 8000
HOST = "127.0.0.1"
WRK_THREADS = 4
WRK_CONNECTIONS = 100
WRK_DURATION = "5s"  # Short duration for quick check, can be increased

SERVER_FILES = {
    "BustAPI": "benchmarks/temp_bustapi.py",
    "Flask": "benchmarks/temp_flask.py",
    "FastAPI": "benchmarks/temp_fastapi.py",
    "Catzilla": "benchmarks/temp_catzilla.py",
}

RUN_COMMANDS = {
    "BustAPI": ["python", "benchmarks/temp_bustapi.py"],
    "Flask": ["gunicorn", "-w", "4", "-b", f"{HOST}:{PORT}", "--access-logfile", "/dev/null", "--error-logfile", "/dev/null", "benchmarks.temp_flask:app"],
    "FastAPI": ["python", "-m", "uvicorn", "benchmarks.temp_fastapi:app", "--host", HOST, "--port", str(PORT), "--workers", "4", "--log-level", "warning", "--no-access-log"],
    "Catzilla": ["python", "benchmarks/temp_catzilla.py"],
}

# Server Code Templates
CODE_BUSTAPI = f"""
from bustapi import BustAPI, jsonify
app = BustAPI()

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/json")
def json_endpoint():
    return jsonify({{"hello": "world"}})

@app.route("/user/<id>")
def user(id):
    return jsonify({{"user_id": int(id)}})

if __name__ == "__main__":
    app.run(host="{HOST}", port={PORT}, workers=4, debug=False)
"""

CODE_FLASK = f"""
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/json")
def json_endpoint():
    return jsonify({{"hello": "world"}})

@app.route("/user/<id>")
def user(id):
    return jsonify({{"user_id": int(id)}})
"""

CODE_FASTAPI = f"""
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, JSONResponse
app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
def index():
    return "Hello, World!"

@app.get("/json")
def json_endpoint():
    return JSONResponse({{"hello": "world"}})

@app.get("/user/{{id}}")
def user(id: int):
    return JSONResponse({{"user_id": id}})
"""

CODE_CATZILLA = f"""
from catzilla import Catzilla, Request, Response, JSONResponse
app = Catzilla(production=True, log_requests=False)

@app.get("/")
def index(request: Request) -> Response:
    return Response("Hello, World!")

@app.get("/json")
def json_endpoint(request: Request) -> Response:
    return JSONResponse({{"hello": "world"}})

@app.get("/user/{{id}}")
def user(request, id: int) -> Response:
    return JSONResponse({{"user_id": id}})

if __name__ == "__main__":
    app.listen(host="{HOST}", port={PORT})
"""

@dataclass
class BenchmarkResult:
    framework: str
    endpoint: str
    requests_sec: float
    latency_ms: float
    cpu_percent: float
    ram_mb: float

class ResourceMonitor:
    def __init__(self, pid: int):
        self.process = psutil.Process(pid)
        self.cpu_samples = []
        self.ram_samples = []
        self.running = False
        self.thread = None
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            
    def _monitor(self):
        # Initial CPU call for main process
        try:
            self.process.cpu_percent()
        except: pass
        
        children_cache = {} # pid -> process_obj

        while self.running:
            try:
                # Main process
                cpu = self.process.cpu_percent()
                mem = self.process.memory_info().rss
                
                # Children
                try:
                    current_children = self.process.children(recursive=True)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    current_children = []

                # Update cache
                current_pids = {p.pid for p in current_children}
                
                # Remove dead
                for pid in list(children_cache.keys()):
                    if pid not in current_pids:
                        del children_cache[pid]
                
                # Add new and sum
                for child in current_children:
                    if child.pid not in children_cache:
                        children_cache[child.pid] = child
                        # Init CPU counter
                        try: child.cpu_percent()
                        except: pass
                    
                    try:
                        c_proc = children_cache[child.pid]
                        # Verify it's still running
                        if c_proc.is_running():
                            cpu += c_proc.cpu_percent()
                            mem += c_proc.memory_info().rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                self.cpu_samples.append(cpu)
                self.ram_samples.append(mem / 1024 / 1024) # MB
                
                time.sleep(0.1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break

    def get_stats(self):
        if not self.cpu_samples: return 0.0, 0.0
        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples)
        max_ram = max(self.ram_samples)
        return avg_cpu, max_ram

def create_server_files():
    print("📝 Creating temporary server files...")
    with open(SERVER_FILES["BustAPI"], "w") as f: f.write(CODE_BUSTAPI)
    with open(SERVER_FILES["Flask"], "w") as f: f.write(CODE_FLASK)
    with open(SERVER_FILES["FastAPI"], "w") as f: f.write(CODE_FASTAPI)
    with open(SERVER_FILES["Catzilla"], "w") as f: f.write(CODE_CATZILLA)

def clean_server_files():
    print("🧹 Cleaning up...")
    for f in SERVER_FILES.values():
        if os.path.exists(f):
            os.remove(f)

def run_wrk(endpoint: str) -> Optional[Dict]:
    url = f"http://{HOST}:{PORT}{endpoint}"
    cmd = ["wrk", "-t", str(WRK_THREADS), "-c", str(WRK_CONNECTIONS), "-d", WRK_DURATION, "--latency", url]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ wrk failed: {result.stderr}")
            return None
        
        # Parse wrk output
        output = result.stdout
        rps = 0.0
        latency = 0.0
        
        for line in output.splitlines():
            if "Requests/sec:" in line:
                rps = float(line.split(":")[1].strip())
            if "Latency" in line and "Avg" in line:
                # This is tricky because wrk output format varies.
                # Assuming standard format: "Latency    1.23ms ..."
                pass
        
        return {"rps": rps, "raw": output}
    except FileNotFoundError:
        print("❌ wrk not found. Please install wrk.")
        sys.exit(1)

def benchmark_framework(name: str):
    print(f"\n🚀 Benchmarking {name}...")
    
    # Start Server
    print(f"   Cleaning port {PORT}...")
    subprocess.run(f"fuser -k {PORT}/tcp", shell=True, stderr=subprocess.DEVNULL)
    time.sleep(1)

    cmd = RUN_COMMANDS[name]
    # Use uv run to ensure dependencies are found
    if cmd[0] == "python":
        final_cmd = ["uv", "run"] + cmd
    else:
        # e.g. gunicorn
        final_cmd = ["uv", "run"] + cmd
        
    print(f"   Starting: {' '.join(final_cmd)}")
    
    out_file = open(f"stdout_{name}.txt", "w")
    err_file = open(f"stderr_{name}.txt", "w")
    
    proc = subprocess.Popen(
        final_cmd,
        cwd=os.getcwd(),
        stdout=out_file,
        stderr=err_file,
        preexec_fn=os.setsid 
    )
    
    time.sleep(3) # Give it time to warm up
    
    # Initialize monitor
    monitor = ResourceMonitor(proc.pid)
    monitor.start()
    
    results = []
    try:
        endpoints = ["/", "/json", "/user/10"]
        for ep in endpoints:
            print(f"   Measuring {ep}...", end="", flush=True)
            res = run_wrk(ep)
            if res:
                # Get current stats (snapshot-ish)
                # Actually, monitor is running continuously.
                # We can just check stats at end, or maybe we want independent stats per endpoint?
                # For simplicity, let's keep monitor running for the whole suite of endpoints
                # and just report the average usage during that specific test?
                # No, ResourceMonitor collects all history. 
                # Let's Restart monitor for each endpoint for better granularity.
                pass
            
            # RESTART MONITOR STRATEGY for per-endpoint stats
            monitor.stop()
            cpu, ram = monitor.get_stats()
            # Clear samples
            monitor.cpu_samples = []
            monitor.ram_samples = []
            monitor.start() # Restart
            
            if res:
                print(f" {res['rps']:.2f} req/sec, CPU: {cpu:.1f}%, RAM: {ram:.1f}MB")
                results.append(BenchmarkResult(name, ep, res['rps'], 0.0, cpu, ram))
            else:
                print(" Failed")
                # Print server output for debugging
                print(f"--- {name} stdout ---")
                try: 
                    print(open(f"stdout_{name}.txt").read())
                except: pass
                print(f"--- {name} stderr ---")
                try: 
                    print(open(f"stderr_{name}.txt").read())
                except: pass
    finally:
        monitor.stop()
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        proc.wait()
        time.sleep(1) # Cooldown
        
    return results

def main():
    if not shutil.which("wrk"):
        print("❌ Error: 'wrk' tool is required. Please install it (e.g., sudo apt install wrk).")
        return

    create_server_files()
    
    all_results = []
    
    try:
        frameworks = ["BustAPI", "Flask", "FastAPI", "Catzilla"]
        for fw in frameworks:
            fw_results = benchmark_framework(fw)
            all_results.extend(fw_results)
            
        # Generate Markdown Report
        report_lines = []
        report_lines.append("# 🚀 Web Framework Benchmark Results")
        report_lines.append("")
        report_lines.append(f"**Date:** {time.strftime('%Y-%m-%d')}")
        report_lines.append(f"**Tool:** `benchmarks/run_comparison_auto.py`")
        report_lines.append(f"**Config:** {WRK_THREADS} threads, {WRK_CONNECTIONS} connections, {WRK_DURATION} duration")
        report_lines.append("")
        report_lines.append("## 📊 Summary (Requests/sec)")
        report_lines.append("")
        
        # Table Header
        headers = ["Endpoint", "Metric"] + frameworks
        report_lines.append("| " + " | ".join(headers) + " |")
        report_lines.append("|" + "|".join(["-" * len(h) for h in headers]) + "|")
        
        # Table Rows
        endpoints = ["/", "/json", "/user/10"]
        for ep in endpoints:
            # Row 1: RPS
            row_rps = [f"**{ep}**", "Req/Sec"]
            
            # Row 2: CPU
            row_cpu = ["", "CPU %"]
            
            # Row 3: RAM
            row_ram = ["", "RAM (MB)"]
            
            for fw in frameworks:
                match = next((r for r in all_results if r.framework == fw and r.endpoint == ep), None)
                if match:
                    # RPS Handling
                    val_str = f"{match.requests_sec:,.0f}"
                    # Check if winner
                    row_values = [
                        (next((r for r in all_results if r.framework == f and r.endpoint == ep), None).requests_sec) 
                        for f in frameworks 
                        if next((r for r in all_results if r.framework == f and r.endpoint == ep), None)
                    ]
                    if match.requests_sec == max(row_values):
                        val_str = f"**{val_str}**"
                    row_rps.append(val_str)
                    
                    row_cpu.append(f"{match.cpu_percent:.1f}%")
                    row_ram.append(f"{match.ram_mb:.1f}")
                else:
                    row_rps.append("N/A")
                    row_cpu.append("N/A")
                    row_ram.append("N/A")
            
            report_lines.append("| " + " | ".join(row_rps) + " |")
            report_lines.append("| " + " | ".join(row_cpu) + " |")
            report_lines.append("| " + " | ".join(row_ram) + " |")
            # Separate sections
            report_lines.append(f"| | | {' | '.join(['---'] * len(frameworks))} |")

        report_lines.append("")
        report_lines.append("## 🏃 How to Run")
        report_lines.append("")
        report_lines.append("```bash")
        report_lines.append("# Clean ports")
        report_lines.append("fuser -k 8000/tcp")
        report_lines.append("")
        report_lines.append("# Run automated benchmark")
        report_lines.append("uv run --extra benchmarks benchmarks/run_comparison_auto.py")
        report_lines.append("```")
        
        report_content = "\n".join(report_lines)
        print("\n\n" + report_content)
        
        # Write to README.md
        with open("benchmarks/README.md", "w") as f:
            f.write(report_content)
        print("\n✅ Updated benchmarks/README.md")
            
    finally:
        clean_server_files()

if __name__ == "__main__":
    main()
