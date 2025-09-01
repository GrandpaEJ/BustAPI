#!/usr/bin/env python3
"""
Framework Comparison Benchmark

Compare BustAPI performance with Flask and FastAPI.
"""

import json
import subprocess
import sys
import time
from typing import Dict, List

import requests


class FrameworkComparison:
    """Compare performance across different frameworks."""

    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.results = {}

    def run_simple_benchmark(self, duration: int = 10, concurrent: int = 50) -> Dict:
        """Run a simple benchmark test."""
        print(f"Running {duration}s benchmark with {concurrent} concurrent requests...")

        import threading
        from concurrent.futures import ThreadPoolExecutor

        start_time = time.time()
        end_time = start_time + duration

        total_requests = 0
        total_errors = 0
        response_times = []
        lock = threading.Lock()

        def make_request():
            nonlocal total_requests, total_errors
            try:
                req_start = time.time()
                response = requests.get(self.base_url, timeout=5)
                req_end = time.time()

                with lock:
                    if response.status_code == 200:
                        total_requests += 1
                        response_times.append(req_end - req_start)
                    else:
                        total_errors += 1

            except Exception:
                with lock:
                    total_errors += 1

        with ThreadPoolExecutor(max_workers=concurrent) as executor:
            while time.time() < end_time:
                futures = []
                batch_size = min(concurrent, 20)

                for _ in range(batch_size):
                    if time.time() >= end_time:
                        break
                    futures.append(executor.submit(make_request))

                for future in futures:
                    future.result()

        actual_duration = time.time() - start_time
        rps = total_requests / actual_duration if actual_duration > 0 else 0

        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        return {
            "rps": round(rps, 2),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "duration": round(actual_duration, 2),
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "error_rate": (
                round(total_errors / (total_requests + total_errors) * 100, 2)
                if (total_requests + total_errors) > 0
                else 0
            ),
        }

    def test_framework(self, framework_name: str) -> Dict:
        """Test a specific framework."""
        print(f"\n🧪 Testing {framework_name}...")

        # Check if server is running
        try:
            response = requests.get(self.base_url, timeout=5)
            print(f"✅ {framework_name} server is running")
        except requests.exceptions.RequestException:
            print(f"❌ {framework_name} server is not running")
            return {"error": f"{framework_name} server not available"}

        # Run benchmark
        results = self.run_simple_benchmark(duration=15, concurrent=100)
        results["framework"] = framework_name
        results["timestamp"] = time.time()

        return results

    def compare_frameworks(self) -> Dict:
        """Compare all frameworks."""
        print("🏁 Framework Performance Comparison")
        print("=" * 50)

        comparison_results = {
            "timestamp": time.time(),
            "test_duration": 15,
            "concurrent_requests": 100,
            "frameworks": {},
        }

        frameworks = ["BustAPI", "Flask", "FastAPI"]

        for framework in frameworks:
            input(f"\n⏸️ Start {framework} server and press Enter to continue...")
            result = self.test_framework(framework)
            comparison_results["frameworks"][framework] = result

        return comparison_results

    def print_comparison(self, results: Dict):
        """Print comparison results."""
        print("\n" + "=" * 70)
        print("📊 FRAMEWORK PERFORMANCE COMPARISON")
        print("=" * 70)

        frameworks = results["frameworks"]

        # Print individual results
        for framework, result in frameworks.items():
            if "error" in result:
                print(f"\n❌ {framework}: {result['error']}")
                continue

            print(f"\n🚀 {framework} Results:")
            print(f"   📈 Requests/sec: {result['rps']}")
            print(f"   📊 Total requests: {result['total_requests']}")
            print(f"   ⏱️ Avg response time: {result['avg_response_time_ms']}ms")
            print(f"   ❌ Error rate: {result['error_rate']}%")

        # Find best performer
        valid_frameworks = {k: v for k, v in frameworks.items() if "error" not in v}

        if len(valid_frameworks) > 1:
            print(f"\n🏆 PERFORMANCE RANKING:")
            sorted_frameworks = sorted(
                valid_frameworks.items(), key=lambda x: x[1]["rps"], reverse=True
            )

            for i, (framework, result) in enumerate(sorted_frameworks, 1):
                if i == 1:
                    print(f"   🥇 {framework}: {result['rps']} RPS")
                elif i == 2:
                    print(f"   🥈 {framework}: {result['rps']} RPS")
                elif i == 3:
                    print(f"   🥉 {framework}: {result['rps']} RPS")
                else:
                    print(f"   {i}. {framework}: {result['rps']} RPS")

            # Calculate improvements
            best_rps = sorted_frameworks[0][1]["rps"]
            print(f"\n📈 PERFORMANCE IMPROVEMENTS:")

            for framework, result in sorted_frameworks[1:]:
                improvement = ((best_rps - result["rps"]) / result["rps"]) * 100
                print(
                    f"   {sorted_frameworks[0][0]} is {improvement:.1f}% faster than {framework}"
                )

        print("\n" + "=" * 70)


def create_flask_server():
    """Create a Flask server for comparison."""
    flask_code = """
from flask import Flask, jsonify
import time

app = Flask(__name__)

users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
]

@app.route('/')
def root():
    return jsonify({
        'message': 'Flask Benchmark Server',
        'version': '1.0.0',
        'timestamp': time.time(),
        'status': 'running'
    })

@app.route('/api/test')
def api_test():
    return jsonify({
        'test': True,
        'framework': 'Flask',
        'performance': 'baseline',
        'timestamp': time.time()
    })

@app.route('/api/users')
def get_users():
    return jsonify({
        'users': users,
        'count': len(users),
        'timestamp': time.time()
    })

if __name__ == '__main__':
    print("🚀 Starting Flask Benchmark Server...")
    app.run(host='127.0.0.1', port=8000, debug=False)
"""

    with open("benchmarks/flask_server.py", "w") as f:
        f.write(flask_code)

    print("📝 Created benchmarks/flask_server.py")


def create_fastapi_server():
    """Create a FastAPI server for comparison."""
    fastapi_code = """
from fastapi import FastAPI
import time
import uvicorn

app = FastAPI(title="FastAPI Benchmark Server", version="1.0.0")

users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
]

@app.get("/")
def root():
    return {
        'message': 'FastAPI Benchmark Server',
        'version': '1.0.0',
        'timestamp': time.time(),
        'status': 'running'
    }

@app.get("/api/test")
def api_test():
    return {
        'test': True,
        'framework': 'FastAPI',
        'performance': 'async',
        'timestamp': time.time()
    }

@app.get("/api/users")
def get_users():
    return {
        'users': users,
        'count': len(users),
        'timestamp': time.time()
    }

if __name__ == '__main__':
    print("🚀 Starting FastAPI Benchmark Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
"""

    with open("benchmarks/fastapi_server.py", "w") as f:
        f.write(fastapi_code)

    print("📝 Created benchmarks/fastapi_server.py")


def main():
    """Main comparison execution."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Framework Performance Comparison")
        print(
            "Usage: python framework_comparison.py [--create-servers] [--save-results]"
        )
        print("\nThis script compares BustAPI, Flask, and FastAPI performance.")
        return

    if len(sys.argv) > 1 and "--create-servers" in sys.argv:
        print("📝 Creating comparison server files...")
        create_flask_server()
        create_fastapi_server()
        print("✅ Server files created!")
        print("\nTo run comparison:")
        print("1. Start BustAPI: python benchmarks/benchmark_server.py")
        print("2. Start Flask: python benchmarks/flask_server.py")
        print("3. Start FastAPI: python benchmarks/fastapi_server.py")
        print("4. Run comparison: python benchmarks/framework_comparison.py")
        return

    # Run comparison
    comparison = FrameworkComparison()
    results = comparison.compare_frameworks()

    # Print results
    comparison.print_comparison(results)

    # Save results if requested
    if len(sys.argv) > 1 and "--save-results" in sys.argv:
        filename = f"comparison_results_{int(time.time())}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {filename}")


if __name__ == "__main__":
    main()
