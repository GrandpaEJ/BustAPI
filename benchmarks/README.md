# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2025-12-10 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-36-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.13.11`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI | Flask | FastAPI | Catzilla |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | 🥇 **13,719** | **2,822** | **1,891** | **9,102** |
|  | ⏱️ Avg Latency | 7.55ms | 34.98ms | 53.67ms | 13.85ms |
|  | 📉 Max Latency | 60.97ms | 58.37ms | 223.33ms | 467.80ms |
|  | 📦 Transfer | 1.69 MB/s | 0.45 MB/s | 0.27 MB/s | 1.28 MB/s |
|  | 🔥 CPU Usage | 154% | 372% | 214% | 98% |
|  | 🧠 RAM Usage | 57.0 MB | 182.7 MB | 264.9 MB | 460.4 MB |
| | | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **9,502** | **4,968** | **2,082** | **9,187** |
|  | ⏱️ Avg Latency | 10.58ms | 20.11ms | 47.18ms | 11.14ms |
|  | 📉 Max Latency | 59.66ms | 68.46ms | 118.53ms | 208.34ms |
|  | 📦 Transfer | 1.14 MB/s | 0.77 MB/s | 0.28 MB/s | 0.99 MB/s |
|  | 🔥 CPU Usage | 150% | 377% | 214% | 98% |
|  | 🧠 RAM Usage | 57.3 MB | 182.9 MB | 266.4 MB | 872.0 MB |
| | | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | **8,532** | **3,426** | **1,964** | 🥇 **8,946** |
|  | ⏱️ Avg Latency | 11.75ms | 28.81ms | 50.51ms | 11.48ms |
|  | 📉 Max Latency | 39.79ms | 63.60ms | 120.89ms | 235.01ms |
|  | 📦 Transfer | 1.00 MB/s | 0.52 MB/s | 0.26 MB/s | 1.26 MB/s |
|  | 🔥 CPU Usage | 151% | 367% | 209% | 98% |
|  | 🧠 RAM Usage | 57.3 MB | 182.8 MB | 267.8 MB | 1279.1 MB |
| | | --- | --- | --- | --- |

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```