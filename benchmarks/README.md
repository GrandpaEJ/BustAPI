# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2026-01-06 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-37-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.13.11`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI | Catzilla | Flask | FastAPI |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | 🥇 **27,597** | **13,581** | **8,252** | **2,005** |
|  | ⏱️ Avg Latency | 3.63ms | 7.80ms | 12.33ms | 48.98ms |
|  | 📉 Max Latency | 23.49ms | 206.56ms | 43.93ms | 136.95ms |
|  | 📦 Transfer | 3.18 MB/s | 1.92 MB/s | 1.31 MB/s | 0.28 MB/s |
|  | 🔥 CPU Usage | 154% | 98% | 389% | 201% |
|  | 🧠 RAM Usage | 24.8 MB | 627.0 MB | 159.4 MB | 232.0 MB |
| | | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **21,405** | **8,992** | **5,249** | **1,990** |
|  | ⏱️ Avg Latency | 4.72ms | 11.31ms | 18.91ms | 49.93ms |
|  | 📉 Max Latency | 40.64ms | 195.92ms | 49.14ms | 105.61ms |
|  | 📦 Transfer | 2.57 MB/s | 0.97 MB/s | 0.82 MB/s | 0.27 MB/s |
|  | 🔥 CPU Usage | 139% | 98% | 384% | 202% |
|  | 🧠 RAM Usage | 25.1 MB | 1031.1 MB | 159.4 MB | 234.2 MB |
| | | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **11,963** | **7,618** | **6,210** | **1,971** |
|  | ⏱️ Avg Latency | 8.42ms | 14.89ms | 16.25ms | 50.41ms |
|  | 📉 Max Latency | 39.41ms | 417.78ms | 58.89ms | 106.55ms |
|  | 📦 Transfer | 1.40 MB/s | 1.08 MB/s | 0.95 MB/s | 0.26 MB/s |
|  | 🔥 CPU Usage | 132% | 98% | 497% | 214% |
|  | 🧠 RAM Usage | 25.3 MB | 1378.3 MB | 159.5 MB | 235.4 MB |
| | | --- | --- | --- | --- |

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```