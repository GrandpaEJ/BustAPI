# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2025-12-11 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-36-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.11.13`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI | Flask | FastAPI |
| :--- | :--- | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | 🥇 **16,311** | **2,603** | **2,022** |
|  | ⏱️ Avg Latency | 6.11ms | 37.70ms | 48.80ms |
|  | 📉 Max Latency | 27.57ms | 77.00ms | 138.96ms |
|  | 📦 Transfer | 1.88 MB/s | 0.41 MB/s | 0.29 MB/s |
|  | 🔥 CPU Usage | 155% | 395% | 241% |
|  | 🧠 RAM Usage | 67.5 MB | 202.4 MB | 292.7 MB |
| | | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **8,828** | **3,314** | **2,134** |
|  | ⏱️ Avg Latency | 11.49ms | 29.76ms | 46.50ms |
|  | 📉 Max Latency | 54.26ms | 49.83ms | 102.75ms |
|  | 📦 Transfer | 1.06 MB/s | 0.52 MB/s | 0.29 MB/s |
|  | 🔥 CPU Usage | 125% | 365% | 203% |
|  | 🧠 RAM Usage | 67.9 MB | 202.6 MB | 293.2 MB |
| | | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **9,555** | **4,179** | **1,901** |
|  | ⏱️ Avg Latency | 10.52ms | 23.63ms | 52.33ms |
|  | 📉 Max Latency | 42.81ms | 49.88ms | 135.15ms |
|  | 📦 Transfer | 1.12 MB/s | 0.64 MB/s | 0.25 MB/s |
|  | 🔥 CPU Usage | 133% | 370% | 200% |
|  | 🧠 RAM Usage | 67.8 MB | 202.4 MB | 293.4 MB |
| | | --- | --- | --- |

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```