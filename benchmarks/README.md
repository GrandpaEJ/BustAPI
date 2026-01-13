# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2026-01-14 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-37-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.13.11`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI (1w) | Catzilla (1w) | Flask (4w) | FastAPI (4w) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | 🥇 **18,511** | **10,532** | **4,988** | **1,999** |
|  | ⏱️ Avg Latency | 5.50ms | 13.98ms | 19.97ms | 49.73ms |
|  | 📉 Max Latency | 35.94ms | 471.50ms | 82.64ms | 111.38ms |
|  | 📦 Transfer | 2.14 MB/s | 1.49 MB/s | 0.79 MB/s | 0.28 MB/s |
|  | 🔥 CPU Usage | 97% | 98% | 388% | 270% |
|  | 🧠 RAM Usage | 44.9 MB | 491.7 MB | 158.9 MB | 232.0 MB |
| | | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **15,079** | **11,171** | **4,910** | **2,000** |
|  | ⏱️ Avg Latency | 6.62ms | 9.79ms | 20.17ms | 49.67ms |
|  | 📉 Max Latency | 22.50ms | 262.10ms | 39.43ms | 111.11ms |
|  | 📦 Transfer | 1.81 MB/s | 1.20 MB/s | 0.76 MB/s | 0.27 MB/s |
|  | 🔥 CPU Usage | 97% | 98% | 390% | 220% |
|  | 🧠 RAM Usage | 44.9 MB | 991.4 MB | 158.9 MB | 233.8 MB |
| | | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **13,230** | **11,187** | **4,552** | **1,886** |
|  | ⏱️ Avg Latency | 7.55ms | 11.87ms | 21.86ms | 52.80ms |
|  | 📉 Max Latency | 25.33ms | 419.61ms | 80.67ms | 129.29ms |
|  | 📦 Transfer | 1.55 MB/s | 1.58 MB/s | 0.69 MB/s | 0.25 MB/s |
|  | 🔥 CPU Usage | 97% | 98% | 483% | 213% |
|  | 🧠 RAM Usage | 44.9 MB | 1496.2 MB | 158.9 MB | 234.9 MB |
| | | --- | --- | --- | --- |

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```