#!/usr/bin/env python3
"""
Comprehensive BustAPI Performance Benchmark

This script runs comprehensive performance tests comparing BustAPI with Flask and FastAPI.
"""

import asyncio
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

import requests


class BenchmarkRunner:
    """Comprehensive benchmark runner for web frameworks."""

    def __init__(self):
        self.results = {}
        self.base_url = "http://127.0.0.1:8000"

    def run_wrk_benchmark(
        self, duration: int = 30, connections: int = 100, threads: int = 4
    ) -> Optional[Dict]:
        """Run wrk benchmark if available."""
        try:
            cmd = [
                "wrk",
                "-t",
                str(threads),
                "-c",
                str(connections),
                "-d",
                f"{duration}s",
                "--latency",
                self.base_url,
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=duration + 10
            )

            if result.returncode == 0:
                return self.parse_wrk_output(result.stdout)
            else:
                print(f"wrk failed: {result.stderr}")
                return None

        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("wrk not available or timed out")
            return None

    def parse_wrk_output(self, output: str) -> Dict:
        """Parse wrk output to extract metrics."""
        lines = output.split("\n")
        metrics = {}

        for line in lines:
            if "Requests/sec:" in line:
                metrics["rps"] = float(line.split(":")[1].strip())
            elif "Latency" in line and "avg" in line:
                parts = line.split()
                if len(parts) >= 4:
                    metrics["latency_avg"] = parts[1]
                    metrics["latency_stdev"] = parts[2]
                    metrics["latency_max"] = parts[3]
            elif "requests in" in line:
                parts = line.split()
                metrics["total_requests"] = int(parts[0])
                metrics["duration"] = parts[3]

        return metrics

    def run_python_benchmark(
        self, duration: int = 10, concurrent_requests: int = 100
    ) -> Dict:
        """Run Python-based benchmark using requests."""
        print(
            f"Running Python benchmark for {duration}s with {concurrent_requests} concurrent requests..."
        )

        start_time = time.time()
        end_time = start_time + duration

        total_requests = 0
        total_errors = 0
        response_times = []

        def make_request():
            nonlocal total_requests, total_errors
            try:
                req_start = time.time()
                response = requests.get(self.base_url, timeout=5)
                req_end = time.time()

                if response.status_code == 200:
                    total_requests += 1
                    response_times.append(req_end - req_start)
                else:
                    total_errors += 1

            except Exception:
                total_errors += 1

        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            while time.time() < end_time:
                # Submit batch of requests
                futures = []
                for _ in range(min(concurrent_requests, 50)):  # Batch size
                    if time.time() >= end_time:
                        break
                    futures.append(executor.submit(make_request))

                # Wait for batch to complete
                for future in futures:
                    future.result()

        actual_duration = time.time() - start_time
        rps = total_requests / actual_duration if actual_duration > 0 else 0

        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        return {
            "rps": rps,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "duration": actual_duration,
            "avg_response_time_ms": avg_response_time * 1000,
            "error_rate": (
                total_errors / (total_requests + total_errors)
                if (total_requests + total_errors) > 0
                else 0
            ),
        }

    def test_endpoint_functionality(self) -> Dict:
        """Test basic endpoint functionality."""
        tests = {
            "root": {"url": "/", "expected_status": 200},
            "json_response": {"url": "/api/test", "expected_status": 200},
            "not_found": {"url": "/nonexistent", "expected_status": 404},
        }

        results = {}

        for test_name, test_config in tests.items():
            try:
                response = requests.get(
                    f"{self.base_url}{test_config['url']}", timeout=5
                )
                results[test_name] = {
                    "status_code": response.status_code,
                    "expected": test_config["expected_status"],
                    "passed": response.status_code == test_config["expected_status"],
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                }
            except Exception as e:
                results[test_name] = {"error": str(e), "passed": False}

        return results

    def run_memory_test(self) -> Dict:
        """Test memory usage during load."""
        try:
            import psutil

            # Find the server process (this is approximate)
            server_processes = []
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if "python" in proc.info["name"] and any(
                        "bustapi" in arg for arg in proc.info["cmdline"]
                    ):
                        server_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not server_processes:
                return {"error": "Could not find server process"}

            # Monitor memory during a short load test
            memory_samples = []

            def monitor_memory():
                for _ in range(10):  # 10 samples over 5 seconds
                    try:
                        total_memory = sum(
                            proc.memory_info().rss for proc in server_processes
                        )
                        memory_samples.append(total_memory / 1024 / 1024)  # MB
                        time.sleep(0.5)
                    except:
                        break

            # Start memory monitoring
            import threading

            monitor_thread = threading.Thread(target=monitor_memory)
            monitor_thread.start()

            # Run a quick load test
            self.run_python_benchmark(duration=5, concurrent_requests=50)

            monitor_thread.join()

            if memory_samples:
                return {
                    "avg_memory_mb": sum(memory_samples) / len(memory_samples),
                    "max_memory_mb": max(memory_samples),
                    "min_memory_mb": min(memory_samples),
                    "samples": len(memory_samples),
                }
            else:
                return {"error": "No memory samples collected"}

        except ImportError:
            return {"error": "psutil not available for memory monitoring"}
        except Exception as e:
            return {"error": f"Memory test failed: {str(e)}"}

    def run_comprehensive_benchmark(self) -> Dict:
        """Run all benchmark tests."""
        print("🚀 Starting Comprehensive BustAPI Benchmark")
        print("=" * 60)

        results = {"timestamp": time.time(), "framework": "BustAPI", "version": "0.1.5"}

        # Test basic functionality first
        print("📋 Testing endpoint functionality...")
        results["functionality"] = self.test_endpoint_functionality()

        # Run Python-based benchmark
        print("🐍 Running Python-based performance test...")
        results["python_benchmark"] = self.run_python_benchmark(
            duration=15, concurrent_requests=100
        )

        # Try wrk benchmark if available
        print("⚡ Attempting wrk benchmark...")
        wrk_results = self.run_wrk_benchmark(duration=30, connections=100, threads=4)
        if wrk_results:
            results["wrk_benchmark"] = wrk_results
        else:
            print("⚠️ wrk benchmark not available")

        # Memory test
        print("💾 Running memory usage test...")
        results["memory_test"] = self.run_memory_test()

        return results

    def print_results(self, results: Dict):
        """Print benchmark results in a formatted way."""
        print("\n" + "=" * 60)
        print("📊 BENCHMARK RESULTS")
        print("=" * 60)

        print(f"🚀 Framework: {results['framework']} v{results['version']}")
        print(f"⏰ Timestamp: {time.ctime(results['timestamp'])}")

        # Functionality results
        if "functionality" in results:
            print("\n📋 Functionality Tests:")
            for test_name, test_result in results["functionality"].items():
                status = "✅ PASS" if test_result.get("passed", False) else "❌ FAIL"
                print(f"   {test_name}: {status}")

        # Performance results
        if "python_benchmark" in results:
            perf = results["python_benchmark"]
            print("\n🐍 Python Benchmark Results:")
            print(f"   📈 Requests/sec: {perf['rps']:.2f}")
            print(f"   📊 Total requests: {perf['total_requests']}")
            print(f"   ⏱️ Average response time: {perf['avg_response_time_ms']:.2f}ms")
            print(f"   ❌ Error rate: {perf['error_rate']:.2%}")

        if "wrk_benchmark" in results:
            wrk = results["wrk_benchmark"]
            print("\n⚡ wrk Benchmark Results:")
            print(f"   📈 Requests/sec: {wrk.get('rps', 'N/A')}")
            print(f"   📊 Total requests: {wrk.get('total_requests', 'N/A')}")
            print(f"   ⏱️ Average latency: {wrk.get('latency_avg', 'N/A')}")

        # Memory results
        if "memory_test" in results and "error" not in results["memory_test"]:
            mem = results["memory_test"]
            print("\n💾 Memory Usage:")
            print(f"   📊 Average: {mem['avg_memory_mb']:.2f} MB")
            print(f"   📈 Peak: {mem['max_memory_mb']:.2f} MB")

        print("\n" + "=" * 60)


def main():
    """Main benchmark execution."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("BustAPI Comprehensive Benchmark")
        print("Usage: python comprehensive_benchmark.py [--save-results]")
        print(
            "\nThis script benchmarks a running BustAPI server at http://127.0.0.1:8000"
        )
        print("Make sure your BustAPI server is running before executing this script.")
        return

    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        print(f"✅ Server is running (status: {response.status_code})")
    except requests.exceptions.RequestException:
        print("❌ Server is not running at http://127.0.0.1:8000")
        print("Please start your BustAPI server first.")
        return

    # Run benchmark
    runner = BenchmarkRunner()
    results = runner.run_comprehensive_benchmark()

    # Print results
    runner.print_results(results)

    # Save results if requested
    if len(sys.argv) > 1 and "--save-results" in sys.argv:
        filename = f"benchmark_results_{int(time.time())}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {filename}")


if __name__ == "__main__":
    main()
