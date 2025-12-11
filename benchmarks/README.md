# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2025-12-11 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-36-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.13.11`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI | Flask | FastAPI | Catzilla |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | 🥇 **19,969** | **4,706** | **2,136** | **9,650** |
|  | ⏱️ Avg Latency | 5.01ms | 21.03ms | 46.57ms | 13.16ms |
|  | 📉 Max Latency | 27.77ms | 39.21ms | 110.73ms | 513.04ms |
|  | 📦 Transfer | 2.30 MB/s | 0.74 MB/s | 0.30 MB/s | 1.36 MB/s |
|  | 🔥 CPU Usage | 162% | 386% | 212% | 98% |
|  | 🧠 RAM Usage | 57.0 MB | 200.3 MB | 290.1 MB | 484.8 MB |
| | | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **14,907** | **4,537** | **2,138** | **10,749** |
|  | ⏱️ Avg Latency | 6.70ms | 21.78ms | 46.51ms | 10.04ms |
|  | 📉 Max Latency | 15.73ms | 34.18ms | 111.50ms | 281.63ms |
|  | 📦 Transfer | 1.79 MB/s | 0.71 MB/s | 0.29 MB/s | 1.16 MB/s |
|  | 🔥 CPU Usage | 139% | 389% | 197% | 98% |
|  | 🧠 RAM Usage | 57.3 MB | 200.5 MB | 290.4 MB | 963.4 MB |
| | | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **13,191** | **4,123** | **1,998** | **9,859** |
|  | ⏱️ Avg Latency | 7.59ms | 24.00ms | 50.03ms | 10.82ms |
|  | 📉 Max Latency | 22.59ms | 42.06ms | 146.78ms | 292.29ms |
|  | 📦 Transfer | 1.55 MB/s | 0.63 MB/s | 0.27 MB/s | 1.39 MB/s |
|  | 🔥 CPU Usage | 134% | 388% | 195% | 98% |
|  | 🧠 RAM Usage | 57.4 MB | 200.3 MB | 290.8 MB | 1409.4 MB |
| | | --- | --- | --- | --- |

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```