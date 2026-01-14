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
| **`/`** | 🚀 RPS | 🥇 **24,731** | **9,495** | **4,775** | **1,835** |
|  | ⏱️ Avg Latency | 4.08ms | 11.23ms | 20.67ms | 54.06ms |
|  | 📉 Max Latency | 26.19ms | 274.22ms | 41.55ms | 126.86ms |
|  | 📦 Transfer | 3.04 MB/s | 1.34 MB/s | 0.76 MB/s | 0.26 MB/s |
|  | 🔥 CPU Usage | 96% | 97% | 384% | 216% |
|  | 🧠 RAM Usage | 28.8 MB | 444.3 MB | 159.1 MB | 232.1 MB |
| | | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **23,557** | **10,659** | **4,986** | **1,995** |
|  | ⏱️ Avg Latency | 4.25ms | 14.82ms | 19.84ms | 49.77ms |
|  | 📉 Max Latency | 12.70ms | 514.59ms | 45.84ms | 109.33ms |
|  | 📦 Transfer | 2.81 MB/s | 1.15 MB/s | 0.78 MB/s | 0.27 MB/s |
|  | 🔥 CPU Usage | 96% | 98% | 389% | 209% |
|  | 🧠 RAM Usage | 29.0 MB | 926.6 MB | 159.1 MB | 234.2 MB |
| | | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **13,213** | **9,393** | **4,436** | **1,895** |
|  | ⏱️ Avg Latency | 7.46ms | 11.79ms | 22.31ms | 51.84ms |
|  | 📉 Max Latency | 17.49ms | 332.63ms | 50.01ms | 131.64ms |
|  | 📦 Transfer | 1.54 MB/s | 1.33 MB/s | 0.68 MB/s | 0.25 MB/s |
|  | 🔥 CPU Usage | 97% | 98% | 387% | 199% |
|  | 🧠 RAM Usage | 29.0 MB | 1359.6 MB | 159.1 MB | 235.2 MB |
| | | --- | --- | --- | --- |

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```