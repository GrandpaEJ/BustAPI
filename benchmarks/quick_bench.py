#!/usr/bin/env python3
"""
Quick Benchmark for BustAPI v0.2.0 with Actix-web
Tests both fast (Rust-only) and dynamic (Python) routes
"""

import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import requests

def run_benchmark(url: str, name: str, duration: int = 10, concurrent: int = 100):
    """Run benchmark against a URL."""
    print(f"\n🔥 Testing: {name}")
    print(f"   URL: {url}")
    print(f"   Duration: {duration}s, Concurrency: {concurrent}")
    
    start_time = time.time()
    end_time = start_time + duration
    
    total_success = 0
    total_errors = 0
    response_times = []
    lock = threading.Lock()
    
    def make_request():
        nonlocal total_success, total_errors
        try:
            req_start = time.time()
            response = requests.get(url, timeout=5)
            req_end = time.time()
            
            with lock:
                if response.status_code == 200:
                    total_success += 1
                    response_times.append(req_end - req_start)
                else:
                    total_errors += 1
        except Exception:
            with lock:
                total_errors += 1
    
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        while time.time() < end_time:
            futures = []
            batch_size = min(concurrent, 50)
            
            for _ in range(batch_size):
                if time.time() >= end_time:
                    break
                futures.append(executor.submit(make_request))
            
            for future in futures:
                try:
                    future.result(timeout=1)
                except:
                    pass
    
    actual_duration = time.time() - start_time
    rps = total_success / actual_duration if actual_duration > 0 else 0
    avg_latency = sum(response_times) / len(response_times) * 1000 if response_times else 0
    
    result = {
        'name': name,
        'success': total_success,
        'errors': total_errors,
        'rps': round(rps, 2),
        'avg_latency_ms': round(avg_latency, 2),
        'duration': round(actual_duration, 2)
    }
    
    print(f"   ✅ Success: {total_success}, Errors: {total_errors}")
    print(f"   📈 RPS: {rps:.2f}")
    print(f"   ⏱️  Latency: {avg_latency:.2f}ms")
    
    return result


def main():
    print("=" * 60)
    print("🚀 BustAPI v0.2.0 Benchmark (Actix-web + Python 3.13)")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5090"
    
    # Check if server is running
    try:
        response = requests.get(base_url, timeout=2)
        print(f"\n✅ Server is running at {base_url}")
    except:
        print(f"\n❌ Server not running! Start it first:")
        print("   uv run examples/hello_world.py")
        sys.exit(1)
    
    results = []
    
    # Test different endpoints
    print("\n" + "-" * 60)
    
    # Test root endpoint (Python handler)
    results.append(run_benchmark(
        f"{base_url}/",
        "Root (Python Handler)",
        duration=10,
        concurrent=100
    ))
    
    # Test JSON endpoint (Python handler)
    results.append(run_benchmark(
        f"{base_url}/json",
        "JSON (Python Handler)", 
        duration=10,
        concurrent=100
    ))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    for r in results:
        print(f"\n{r['name']}:")
        print(f"   RPS: {r['rps']} | Latency: {r['avg_latency_ms']}ms | Success: {r['success']}")
    
    # Save results
    timestamp = int(time.time())
    with open("benchmarks/last_results.txt", "w") as f:
        f.write(f"BustAPI v0.2.0 Benchmark Results\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Backend: Actix-web + PyO3 0.23\n")
        f.write(f"Python: 3.13 (free-threading mode)\n")
        f.write("-" * 40 + "\n")
        for r in results:
            f.write(f"{r}\n")
    
    print(f"\n💾 Results saved to benchmarks/last_results.txt")
    print("=" * 60)


if __name__ == "__main__":
    main()
