# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2026-01-14 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-37-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.13.11`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI (1w) | Catzilla (1w) | Flask (4w) | FastAPI (4w) | Robyn (4w) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | 🥇 **21,025** | **4,776** | **2,125** | **2,773** | **3,994** |
|  | ⏱️ Avg Latency | 4.86ms | 27.53ms | 46.19ms | 36.01ms | 24.93ms |
|  | 📉 Max Latency | 58.75ms | 580.40ms | 94.70ms | 134.33ms | 148.60ms |
|  | 📦 Transfer | 2.58 MB/s | 0.68 MB/s | 0.34 MB/s | 0.39 MB/s | 0.54 MB/s |
|  | 🔥 CPU Usage | 96% | 96% | 340% | 315% | 98% |
|  | 🧠 RAM Usage | 36.5 MB | 228.4 MB | 159.3 MB | 239.1 MB | 45.2 MB |
| | | --- | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **20,304** | **5,114** | **2,324** | **2,693** | **3,527** |
|  | ⏱️ Avg Latency | 4.93ms | 30.10ms | 42.41ms | 37.33ms | 28.21ms |
|  | 📉 Max Latency | 18.90ms | 610.20ms | 88.50ms | 115.60ms | 136.20ms |
|  | 📦 Transfer | 2.50 MB/s | 0.55 MB/s | 0.36 MB/s | 0.37 MB/s | 0.42 MB/s |
|  | 🔥 CPU Usage | 96% | 97% | 341% | 318% | 98% |
|  | 🧠 RAM Usage | 37.2 MB | 455.5 MB | 159.2 MB | 240.2 MB | 46.8 MB |
| | | --- | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **8,679** | **4,764** | **2,149** | **2,176** | **3,681** |
|  | ⏱️ Avg Latency | 11.59ms | 41.99ms | 45.91ms | 45.93ms | 26.92ms |
|  | 📉 Max Latency | 30.20ms | 725.10ms | 112.30ms | 167.40ms | 128.50ms |
|  | 📦 Transfer | 1.02 MB/s | 0.68 MB/s | 0.33 MB/s | 0.28 MB/s | 0.29 MB/s |
|  | 🔥 CPU Usage | 97% | 97% | 328% | 295% | 98% |
|  | 🧠 RAM Usage | 37.4 MB | 652.3 MB | 159.3 MB | 240.5 MB | 47.1 MB |
| | | --- | --- | --- | --- | --- |

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```
