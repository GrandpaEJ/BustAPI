#!/usr/bin/env python3
"""
Automated Framework Comparison Benchmark
BustAPI vs Flask vs FastAPI vs Sanic vs Falcon vs Bottle vs Django vs BlackSheep

Requires: wrk, uv
"""

import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import psutil

# Configuration
PORT = 8000
HOST = "127.0.0.1"
WRK_THREADS = 4
WRK_CONNECTIONS = 100
WRK_DURATION = "3s"  # Short duration for quick check, can be increased


WORKERS_CONFIG = {
    "BustAPI": 4,
    "Flask": 4,
    "FastAPI": 4,
    "Sanic": 4,
    "Falcon": 4,
    "Bottle": 4,
    "Django": 4,
    "BlackSheep": 4,
}

SERVER_FILES = {
    "BustAPI": "benchmarks/temp_bustapi.py",
    "Flask": "benchmarks/temp_flask.py",
    "FastAPI": "benchmarks/temp_fastapi.py",
    "Sanic": "benchmarks/temp_sanic.py",
    "Falcon": "benchmarks/temp_falcon.py",
    "Bottle": "benchmarks/temp_bottle.py",
    "Django": "benchmarks/temp_django.py",
    "BlackSheep": "benchmarks/temp_blacksheep.py",
}

RUN_COMMANDS = {
    "BustAPI": ["python", "benchmarks/temp_bustapi.py"],
    "Flask": [
        "gunicorn",
        "-w",
        str(WORKERS_CONFIG["Flask"]),
        "-b",
        f"{HOST}:{PORT}",
        "--access-logfile",
        "/dev/null",
        "--error-logfile",
        "/dev/null",
        "benchmarks.temp_flask:app",
    ],
    "Robyn": ["python", "benchmarks/temp_robyn.py"],
    "FastAPI": [
        "python",
        "-m",
        "uvicorn",
        "benchmarks.temp_fastapi:app",
        "--host",
        HOST,
        "--port",
        str(PORT),
        "--workers",
        str(WORKERS_CONFIG["FastAPI"]),
        "--log-level",
        "warning",
        "--no-access-log",
    ],
    "Sanic": ["python", "benchmarks/temp_sanic.py"],
    "Falcon": ["python", "benchmarks/temp_falcon.py"],
    "Bottle": ["python", "benchmarks/temp_bottle.py"],
    "Django": ["python", "benchmarks/temp_django.py"],
    "BlackSheep": [
        "python",
        "-m",
        "uvicorn",
        "benchmarks.temp_blacksheep:app",
        "--host",
        HOST,
        "--port",
        str(PORT),
        "--workers",
        str(WORKERS_CONFIG["BlackSheep"]),
        "--log-level",
        "warning",
        "--no-access-log",
    ],
}

# Server Code Templates
CODE_BUSTAPI = f"""
from bustapi import BustAPI, jsonify
app = BustAPI()

# Turbo routes - zero overhead (no request context, sessions, middleware)
@app.turbo_route("/")
def index():
    return "Hello, World!"

@app.turbo_route("/json")
def json_endpoint():
    return {{"hello": "world"}}

# # Typed turbo route for path params (v0.8.0+)
# @app.turbo_route("/user/<int:id>")
# def user(id: int):
#     return {{"user_id": id}}

@app.route("/user/<id>")
def user(id):
    return {{"user_id": int(id)}}

if __name__ == "__main__":
    # 8 workers with os.fork() + SO_REUSEPORT for true multiprocessing
    app.run(host="{HOST}", port={PORT}, workers={WORKERS_CONFIG["BustAPI"]}, debug=False)
"""

CODE_FLASK = """
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/json")
def json_endpoint():
    return jsonify({"hello": "world"})

@app.route("/user/<id>")
def user(id):
    return jsonify({"user_id": int(id)})
"""

CODE_FASTAPI = """
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, JSONResponse
app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
def index():
    return "Hello, World!"

@app.get("/json")
def json_endpoint():
    return JSONResponse({"hello": "world"})

@app.get("/user/{id}")
def user(id: int):
    return JSONResponse({"user_id": id})
"""


CODE_SANIC = f"""
from sanic import Sanic, response

app = Sanic("Benchmark")

@app.route("/")
async def index(request):
    return response.text("Hello, World!")

@app.route("/json")
async def json_endpoint(request):
    return response.json({{"hello": "world"}})

@app.route("/user/<id:int>")
async def user(request, id):
    return response.json({{"user_id": id}})

if __name__ == "__main__":
    app.run(host="{HOST}", port={PORT}, workers={WORKERS_CONFIG["Sanic"]}, access_log=False)
"""

CODE_FALCON = f"""
import falcon
import json

class IndexResource:
    def on_get(self, req, resp):
        resp.text = "Hello, World!"

class JsonResource:
    def on_get(self, req, resp):
        resp.text = json.dumps({{"hello": "world"}})
        resp.content_type = falcon.MEDIA_JSON

class UserResource:
    def on_get(self, req, resp, id):
        resp.text = json.dumps({{"user_id": int(id)}})
        resp.content_type = falcon.MEDIA_JSON

app = falcon.App()
app.add_route("/", IndexResource())
app.add_route("/json", JsonResource())
app.add_route("/user/{{id}}", UserResource())

if __name__ == "__main__":
    import gunicorn.app.base

    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.application = app
            self.options = options or {{}}
            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key, value)

        def load(self):
            return self.application

    options = {{
        "bind": "{HOST}:{PORT}",
        "workers": {WORKERS_CONFIG["Falcon"]},
    }}
    StandaloneApplication(app, options).run()
"""

CODE_BOTTLE = f"""
from bottle import Bottle, run, response
import json

app = Bottle()

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/json")
def json_endpoint():
    response.content_type = 'application/json'
    return json.dumps({{"hello": "world"}})

@app.route("/user/<id:int>")
def user(id):
    response.content_type = 'application/json'
    return json.dumps({{"user_id": id}})

if __name__ == "__main__":
    run(app, host="{HOST}", port={PORT}, server="gunicorn", workers={WORKERS_CONFIG["Bottle"]}, quiet=True)
"""

CODE_DJANGO = f"""
import os
import sys
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse, JsonResponse
from django.urls import path

if not settings.configured:
    settings.configure(
        DEBUG=False,
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=["*"],
    )

def index(request):
    return HttpResponse("Hello, World!")

def json_endpoint(request):
    return JsonResponse({{"hello": "world"}})

def user(request, id):
    return JsonResponse({{"user_id": id}})

urlpatterns = [
    path("", index),
    path("json", json_endpoint),
    path("user/<int:id>", user),
]

application = get_wsgi_application()

if __name__ == "__main__":
    import gunicorn.app.base

    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.application = app
            self.options = options or {{}}
            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key, value)

        def load(self):
            return self.application

    options = {{
        "bind": "{HOST}:{PORT}",
        "workers": {WORKERS_CONFIG["Django"]},
        "accesslog": "-",
        "errorlog": "-",
    }}
    # Mute logs
    open(options["accesslog"], "w").close()
    open(options["errorlog"], "w").close()

    StandaloneApplication(application, options).run()
"""

CODE_BLACKSHEEP = """
from blacksheep import Application, json
import uvicorn

app = Application()

@app.router.get("/")
def index():
    return "Hello, World!"

@app.router.get("/json")
def json_endpoint():
    return json({"hello": "world"})

@app.router.get("/user/:id")
def user(id: int):
    return json({"user_id": id})
"""


@dataclass
class BenchmarkResult:
    framework: str
    endpoint: str
    requests_sec: float
    transfer_sec_mb: float
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
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
        except:
            pass

        children_cache = {}  # pid -> process_obj

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
                        try:
                            child.cpu_percent()
                        except:
                            pass

                    try:
                        c_proc = children_cache[child.pid]
                        # Verify it's still running
                        if c_proc.is_running():
                            cpu += c_proc.cpu_percent()
                            mem += c_proc.memory_info().rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                self.cpu_samples.append(cpu)
                self.ram_samples.append(mem / 1024 / 1024)  # MB

                time.sleep(0.1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break

    def get_stats(self):
        if not self.cpu_samples:
            return 0.0, 0.0
        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples)
        max_ram = max(self.ram_samples)
        return avg_cpu, max_ram


def get_system_info():
    info = {}
    info["os"] = f"{platform.system()} {platform.release()}"
    info["python"] = platform.python_version()

    # CPU Model
    try:
        if platform.system() == "Linux":
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        info["cpu_model"] = line.split(":")[1].strip()
                        break
        else:
            info["cpu_model"] = platform.processor()
    except:
        info["cpu_model"] = "Unknown"

    info["cpu_count"] = psutil.cpu_count(logical=True)
    info["ram_total_gb"] = round(psutil.virtual_memory().total / (1024**3), 1)

    return info


def create_server_files():
    print("📝 Creating temporary server files...")
    with open(SERVER_FILES["BustAPI"], "w") as f:
        f.write(CODE_BUSTAPI)
    with open(SERVER_FILES["Flask"], "w") as f:
        f.write(CODE_FLASK)
    with open(SERVER_FILES["FastAPI"], "w") as f:
        f.write(CODE_FASTAPI)
    with open(SERVER_FILES["Sanic"], "w") as f:
        f.write(CODE_SANIC)
    with open(SERVER_FILES["Falcon"], "w") as f:
        f.write(CODE_FALCON)
    with open(SERVER_FILES["Bottle"], "w") as f:
        f.write(CODE_BOTTLE)
    with open(SERVER_FILES["Django"], "w") as f:
        f.write(CODE_DJANGO)
    with open(SERVER_FILES["BlackSheep"], "w") as f:
        f.write(CODE_BLACKSHEEP)


def clean_server_files():
    print("🧹 Cleaning up...")
    for f in SERVER_FILES.values():
        if os.path.exists(f):
            os.remove(f)


def parse_time(time_str):
    """Convert time string (e.g., '10.50ms', '1s') to ms."""
    time_str = time_str.lower()
    if "us" in time_str:
        return float(time_str.replace("us", "")) / 1000
    if "ms" in time_str:
        return float(time_str.replace("ms", ""))
    if "s" in time_str:
        return float(time_str.replace("s", "")) * 1000
    return float(time_str)


def parse_size(size_str):
    """Convert size string to MB."""
    size_str = size_str.lower()
    if "kb" in size_str:
        return float(size_str.replace("kb", "")) / 1024
    if "mb" in size_str:
        return float(size_str.replace("mb", ""))
    if "gb" in size_str:
        return float(size_str.replace("gb", "")) * 1024
    if "b" in size_str:
        return float(size_str.replace("b", "")) / 1024 / 1024
    return float(size_str)


def run_wrk(endpoint: str) -> Optional[Dict]:
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

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ wrk failed: {result.stderr}")
            return None

        # Parse wrk output
        output = result.stdout

        # Defaults
        data = {
            "rps": 0.0,
            "transfer_mb": 0.0,
            "avg_latency": 0.0,
            "min_latency": 0.0,
            "max_latency": 0.0,
            "raw": output,
        }

        # Parsing using regex for better accuracy
        # Requests/sec:  19634.88
        rps_match = re.search(r"Requests/sec:\s+([\d.]+)", output)
        if rps_match:
            data["rps"] = float(rps_match.group(1))

        # Transfer/sec:      2.42MB
        transfer_match = re.search(r"Transfer/sec:\s+([0-9.]+)(\w+)", output)
        if transfer_match:
            val = float(transfer_match.group(1))
            unit = transfer_match.group(2)
            data["transfer_mb"] = parse_size(f"{val}{unit}")

        # Latency   3.89ms    2.17ms  29.98ms   89.38%
        # Columns: Avg, Stdev, Max, +/- Stdev (approx)
        # Or detailed stats if present.
        # But wrk summary line is usually:
        # Thread Stats   Avg      Stdev     Max   +/- Stdev
        #   Latency     3.89ms    2.17ms  29.98ms   89.38%

        latency_match = re.search(
            r"Latency\s+([\d\.]+\w+)\s+([\d\.]+\w+)\s+([\d\.]+\w+)", output
        )
        if latency_match:
            data["avg_latency"] = parse_time(latency_match.group(1))
            data["max_latency"] = parse_time(latency_match.group(3))
            # Min latency isn't directly in summary line, usually need detailed output or approximation.
            # wrk default doesn't show min in summary table.
            # However some versions output:
            # Latency Distribution
            # 50% 1.2ms ...
            data["min_latency"] = 0.0  # Not reliably available in default summary

        return data
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
    # Use generic command execution
    final_cmd = cmd

    print(f"   Starting: {' '.join(final_cmd)}")

    out_file = open(f"stdout_{name}.txt", "w")
    err_file = open(f"stderr_{name}.txt", "w")

    proc = subprocess.Popen(
        final_cmd,
        cwd=os.getcwd(),
        stdout=out_file,
        stderr=err_file,
        preexec_fn=os.setsid,
    )

    time.sleep(3)  # Give it time to warm up

    # Initialize monitor
    monitor = ResourceMonitor(proc.pid)
    monitor.start()

    results = []
    try:
        endpoints = ["/", "/json", "/user/10"]
        for ep in endpoints:
            print(f"   Measuring {ep}...", end="", flush=True)
            res = run_wrk(ep)

            # Restart monitor for clean stats per endpoint
            monitor.stop()
            cpu, ram = monitor.get_stats()
            # Clear samples
            monitor.cpu_samples = []
            monitor.ram_samples = []
            monitor.start()  # Restart

            if res:
                print(f" {res['rps']:.2f} req/sec, Latency: {res['avg_latency']:.2f}ms")
                results.append(
                    BenchmarkResult(
                        framework=name,
                        endpoint=ep,
                        requests_sec=res["rps"],
                        transfer_sec_mb=res["transfer_mb"],
                        avg_latency_ms=res["avg_latency"],
                        min_latency_ms=res["min_latency"],
                        max_latency_ms=res["max_latency"],
                        cpu_percent=cpu,
                        ram_mb=ram,
                    )
                )
            else:
                print(" Failed")

    finally:
        monitor.stop()
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=5)
        except:
            print(f"   ⚠️ Force killing {name}...")
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                proc.wait(timeout=2)
            except:
                pass
        time.sleep(1)  # Cooldown

    return results


def main():
    if not shutil.which("wrk"):
        print(
            "❌ Error: 'wrk' tool is required. Please install it (e.g., sudo apt install wrk)."
        )
        return

    create_server_files()

    all_results = []

    try:
        frameworks = [
            "BustAPI",
            "Flask",
            "FastAPI",
            "Sanic",
            "Falcon",
            "Bottle",
            "Django",
            "BlackSheep",
        ]

        for fw in frameworks:
            fw_results = benchmark_framework(fw)
            all_results.extend(fw_results)

        # Generate Markdown Report
        sys_info = get_system_info()

        # Generate Graph
        generate_graph(all_results, sys_info)

        report_lines = []
        report_lines.append("# ⚡ Ultimate Web Framework Benchmark")
        report_lines.append("")
        report_lines.append(
            f"> **Date:** {time.strftime('%Y-%m-%d')} | **Tool:** `wrk`"
        )
        report_lines.append("")
        report_lines.append("## 🖥️ System Spec")
        report_lines.append(f"- **OS:** `{sys_info['os']}`")
        report_lines.append(
            f"- **CPU:** `{sys_info['cpu_model']}` ({sys_info['cpu_count']} Cores)"
        )
        report_lines.append(f"- **RAM:** `{sys_info['ram_total_gb']} GB`")
        report_lines.append(f"- **Python:** `{sys_info['python']}`")
        report_lines.append("")
        report_lines.append("## 🏆 Throughput (Requests/sec)")
        report_lines.append("")

        # Throughput Table
        # Throughput Table
        headers = ["Endpoint", "Metrics"] + [
            f"{fw} ({WORKERS_CONFIG[fw]}w)" for fw in frameworks
        ]
        report_lines.append("| " + " | ".join(headers) + " |")
        report_lines.append(
            "| :--- | :--- | " + " | ".join([":---:" for _ in frameworks]) + " |"
        )

        endpoints = ["/", "/json", "/user/10"]

        for ep in endpoints:
            # Metric Rows
            metrics = [
                ("🚀 RPS", lambda r: f"**{r.requests_sec:,.0f}**"),
                ("⏱️ Avg Latency", lambda r: f"{r.avg_latency_ms:.2f}ms"),
                ("📉 Max Latency", lambda r: f"{r.max_latency_ms:.2f}ms"),
                ("📦 Transfer", lambda r: f"{r.transfer_sec_mb:.2f} MB/s"),
                ("🔥 CPU Usage", lambda r: f"{r.cpu_percent:.0f}%"),
                ("🧠 RAM Usage", lambda r: f"{r.ram_mb:.1f} MB"),
            ]

            first_metric = True
            for metric_name, metric_fmt in metrics:
                row = []
                if first_metric:
                    row.append(f"**`{ep}`**")
                else:
                    row.append("")

                row.append(metric_name)

                for fw in frameworks:
                    res = next(
                        (
                            r
                            for r in all_results
                            if r.framework == fw and r.endpoint == ep
                        ),
                        None,
                    )
                    if res:
                        val = metric_fmt(res)
                        # Highlight winner for RPS
                        if metric_name == "🚀 RPS":
                            competitors = [
                                r.requests_sec for r in all_results if r.endpoint == ep
                            ]
                            if res.requests_sec == max(competitors):
                                val = f"🥇 {val}"
                        row.append(val)
                    else:
                        row.append("N/A")

                report_lines.append("| " + " | ".join(row) + " |")
                first_metric = False

            # Divider
            report_lines.append(f"| | | {' | '.join(['---'] * len(frameworks))} |")

        report_lines.append("")
        report_lines.append("## 📊 Performance Comparison")
        report_lines.append("![RPS Comparison](rps_comparison.png)")
        report_lines.append("")
        report_lines.append("## ⚙️ How to Reproduce")
        report_lines.append("```bash")
        report_lines.append(
            "uv run --extra benchmarks benchmarks/run_comparison_auto.py"
        )
        report_lines.append("```")

        report_content = "\n".join(report_lines)
        print("\n\n" + report_content)

        # Write to README.md
        with open("benchmarks/README.md", "w") as f:
            f.write(report_content)
        print("\n✅ Updated benchmarks/README.md")

    finally:
        clean_server_files()


def generate_graph(results: List[BenchmarkResult], sys_info: Dict):
    """Generate RPS comparison graph (Horizontal)."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
    except ImportError:
        print("❌ matplotlib not found. Skipping graph generation.")
        return

    frameworks = sorted({r.framework for r in results})
    endpoints = sorted({r.endpoint for r in results})

    # Setup Colors
    color_map = {
        "BustAPI": "#800000",  # Khoyeri (Maroon)
        "Sanic": "#ff007f",  # Bright Pink
        "BlackSheep": "#333333",  # Dark Grey
        "FastAPI": "#009688",  # Teal
        "Falcon": "#607d8b",  # Blue Grey
        "Bottle": "#9e9e9e",  # Grey
        "Flask": "#34495e",  # Midnight Blue
        "Django": "#0c4b33",  # Django Green
    }

    # Create subplots (one for each endpoint)
    fig, axes = plt.subplots(len(endpoints), 1, figsize=(10, 4 * len(endpoints)))
    if len(endpoints) == 1:
        axes = [axes]

    for i, ep in enumerate(endpoints):
        ax = axes[i]

        # Get data for this endpoint, sorted by RPS ascending (for horizontal graph top-to-bottom feel)
        ep_data = [r for r in results if r.endpoint == ep]
        ep_data.sort(
            key=lambda x: x.requests_sec
        )  # Ascending for barh (bottom is first index)

        names = [r.framework for r in ep_data]
        values = [r.requests_sec for r in ep_data]
        colors = [color_map.get(n, "#999999") for n in names]

        y_pos = range(len(names))

        bars = ax.barh(
            y_pos, values, align="center", color=colors, alpha=0.9, height=0.6
        )
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=10, fontweight="medium")
        ax.invert_yaxis()  # Labels read top-to-bottom -> Highest RPS at top

        # Invert data logic again for correct visual sorting (Top = High RPS)
        # Wait, sorted ascending implies lowest at bottom. If I invert y-axis, lowest becomes top.
        # I want Highest at Top.
        # Sort Ascending: [Low, ..., High].
        # Barh plots index 0 at bottom.
        # So Index 0 = Low (Bottom), Index N = High (Top).
        # Normal barh: High is on Top.
        # So I do NOT need invert_yaxis?
        # NO, usually y-axis 0 is at bottom.
        # Let's test mental model:
        # idx 0: Low RPS. Plot at y=0.
        # idx N: High RPS. Plot at y=N.
        # Result: High RPS is at the top of the chart. Low RPS at bottom.
        # This matches the user's reference image (Long bar at top).
        # BUT, standard text naming order (Top to Bottom) usually matches visual bars.
        # So names should be [Low...High] to match bars.
        # Yes.

        ax.set_xlabel("Requests Per Second (RPS)")
        ax.set_title(f"Endpoint: {ep}", fontsize=12, fontweight="bold", pad=10)
        ax.grid(axis="x", linestyle="--", alpha=0.3)

        # Add values on bars
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + (max(values) * 0.01),
                bar.get_y() + bar.get_height() / 2,
                f"{int(width):,}",
                ha="left",
                va="center",
                fontsize=9,
                fontweight="bold",
                color="#444",
            )

    plt.tight_layout()

    # Add System Info & Config Note (Global Footer)
    info_text = (
        f"Device: {sys_info['cpu_model']} | {sys_info['cpu_count']} Cores | {sys_info['ram_total_gb']}GB RAM\n"
        f"OS: {sys_info['os']} | Python: {sys_info['python']}\n"
        f"Workers: {', '.join([f'{k}:{v}' for k, v in WORKERS_CONFIG.items() if k in frameworks])}"
    )

    # Make room for footer
    plt.subplots_adjust(bottom=0.15)  # Global adjustment

    fig.text(
        0.5,
        0.02,
        info_text,
        ha="center",
        fontsize=9,
        bbox={
            "facecolor": "white",
            "alpha": 0.9,
            "edgecolor": "#ccc",
            "boxstyle": "round,pad=0.5",
        },
    )

    # Save graph
    output_path = "benchmarks/rps_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"\n✅ Graph saved to {output_path}")


if __name__ == "__main__":
    main()
