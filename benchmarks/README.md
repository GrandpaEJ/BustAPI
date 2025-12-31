# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2026-01-01 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-37-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.13.11`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI | Catzilla | Flask | FastAPI |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | 🥇 **25,782** | **15,727** | **6,869** | **1,867** |
|  | ⏱️ Avg Latency | 3.89ms | 6.85ms | 14.45ms | 53.27ms |
|  | 📉 Max Latency | 17.92ms | 217.64ms | 38.54ms | 147.54ms |
|  | 📦 Transfer | 2.98 MB/s | 2.22 MB/s | 1.09 MB/s | 0.26 MB/s |
|  | 🔥 CPU Usage | 157% | 98% | 390% | 236% |
|  | 🧠 RAM Usage | 24.3 MB | 718.9 MB | 160.3 MB | 237.7 MB |
| | | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **21,440** | **14,139** | **7,587** | **1,930** |
|  | ⏱️ Avg Latency | 4.65ms | 8.61ms | 14.00ms | 51.51ms |
|  | 📉 Max Latency | 13.14ms | 297.39ms | 69.67ms | 123.09ms |
|  | 📦 Transfer | 2.58 MB/s | 1.52 MB/s | 1.18 MB/s | 0.26 MB/s |
|  | 🔥 CPU Usage | 142% | 98% | 380% | 208% |
|  | 🧠 RAM Usage | 24.7 MB | 1372.2 MB | 160.3 MB | 240.6 MB |
| | | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **14,834** | **12,989** | **4,010** | **1,841** |
|  | ⏱️ Avg Latency | 6.81ms | 7.96ms | 24.70ms | 53.30ms |
|  | 📉 Max Latency | 41.08ms | 183.29ms | 39.72ms | 125.76ms |
|  | 📦 Transfer | 1.74 MB/s | 1.83 MB/s | 0.61 MB/s | 0.25 MB/s |
|  | 🔥 CPU Usage | 134% | 98% | 389% | 220% |
|  | 🧠 RAM Usage | 24.8 MB | 1964.2 MB | 160.4 MB | 242.0 MB |
| | | --- | --- | --- | --- |

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```