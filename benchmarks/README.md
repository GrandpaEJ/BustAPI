# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2025-12-11 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-36-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.11.13`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI | Flask | FastAPI | Catzilla |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | 🥇 **18,015** | **3,560** | **2,039** | **9,953** |
|  | ⏱️ Avg Latency | 5.67ms | 27.71ms | 48.91ms | 12.96ms |
|  | 📉 Max Latency | 73.26ms | 71.26ms | 118.88ms | 452.51ms |
|  | 📦 Transfer | 2.08 MB/s | 0.56 MB/s | 0.29 MB/s | 1.40 MB/s |
|  | 🔥 CPU Usage | 161% | 358% | 309% | 97% |
|  | 🧠 RAM Usage | 67.1 MB | 201.5 MB | 295.2 MB | 502.0 MB |
| | | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **11,660** | **4,156** | **2,112** | **11,290** |
|  | ⏱️ Avg Latency | 8.57ms | 23.77ms | 47.07ms | 8.96ms |
|  | 📉 Max Latency | 28.94ms | 42.93ms | 91.49ms | 151.01ms |
|  | 📦 Transfer | 1.40 MB/s | 0.65 MB/s | 0.29 MB/s | 1.22 MB/s |
|  | 🔥 CPU Usage | 139% | 378% | 193% | 98% |
|  | 🧠 RAM Usage | 67.4 MB | 201.7 MB | 295.7 MB | 1001.6 MB |
| | | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | **9,197** | **3,690** | **1,976** | 🥇 **10,249** |
|  | ⏱️ Avg Latency | 11.02ms | 26.72ms | 50.30ms | 14.44ms |
|  | 📉 Max Latency | 50.08ms | 59.05ms | 117.82ms | 494.67ms |
|  | 📦 Transfer | 1.08 MB/s | 0.56 MB/s | 0.26 MB/s | 1.45 MB/s |
|  | 🔥 CPU Usage | 131% | 373% | 201% | 98% |
|  | 🧠 RAM Usage | 67.4 MB | 201.5 MB | 296.1 MB | 1475.4 MB |
| | | --- | --- | --- | --- |

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```