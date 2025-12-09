
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
    
    # Wait for startup
    time.sleep(3) # Give it time to warm up
    
    results = []
    try:
        endpoints = ["/", "/json", "/user/10"]
        for ep in endpoints:
            print(f"   Measuring {ep}...", end="", flush=True)
            res = run_wrk(ep)
            if res:
                print(f" {res['rps']:.2f} req/sec")
                results.append(BenchmarkResult(name, ep, res["rps"], 0.0))
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
            
        # Print Report
        print("\n" + "="*60)
        print(f"{'Framework':<15} | {'Endpoint':<10} | {'Req/Sec':<15}")
        print("-" * 60)
        
        # Sort by endpoint then RPS
        endpoints = ["/", "/json", "/user/10"]
        for ep in endpoints:
            ep_results = [r for r in all_results if r.endpoint == ep]
            ep_results.sort(key=lambda x: x.requests_sec, reverse=True)
            
            for r in ep_results:
                print(f"{r.framework:<15} | {r.endpoint:<10} | {r.requests_sec:,.2f}")
            print("-" * 60)
            
    finally:
        clean_server_files()

if __name__ == "__main__":
    main()
