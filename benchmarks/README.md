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
| **`/`** | 🚀 RPS | 🥇 **17,743** | **8,161** | **3,490** | **1,894** |
|  | ⏱️ Avg Latency | 5.67ms | 12.78ms | 28.33ms | 52.94ms |
|  | 📉 Max Latency | 36.13ms | 277.37ms | 41.22ms | 168.64ms |
|  | 📦 Transfer | 2.18 MB/s | 1.15 MB/s | 0.55 MB/s | 0.27 MB/s |
|  | 🔥 CPU Usage | 96% | 98% | 387% | 225% |
|  | 🧠 RAM Usage | 38.6 MB | 385.0 MB | 177.4 MB | 259.5 MB |
| | | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **18,840** | **8,679** | **3,338** | **1,912** |
|  | ⏱️ Avg Latency | 5.30ms | 11.54ms | 29.66ms | 52.03ms |
|  | 📉 Max Latency | 10.19ms | 195.05ms | 48.81ms | 108.38ms |
|  | 📦 Transfer | 2.25 MB/s | 0.94 MB/s | 0.52 MB/s | 0.26 MB/s |
|  | 🔥 CPU Usage | 96% | 98% | 384% | 224% |
|  | 🧠 RAM Usage | 38.6 MB | 781.6 MB | 177.5 MB | 260.2 MB |
| | | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **10,372** | **7,907** | **3,081** | **1,917** |
|  | ⏱️ Avg Latency | 9.66ms | 16.35ms | 32.08ms | 51.14ms |
|  | 📉 Max Latency | 40.64ms | 514.98ms | 74.57ms | 114.55ms |
|  | 📦 Transfer | 1.22 MB/s | 1.12 MB/s | 0.47 MB/s | 0.26 MB/s |
|  | 🔥 CPU Usage | 97% | 98% | 377% | 212% |
|  | 🧠 RAM Usage | 38.9 MB | 1135.2 MB | 177.5 MB | 260.3 MB |
| | | --- | --- | --- | --- |

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```