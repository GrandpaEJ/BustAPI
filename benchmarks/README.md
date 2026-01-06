# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2026-01-06 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-37-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.13.11`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI (1w) | Catzilla (1w) | Flask (4w) | FastAPI (4w) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | 🥇 **18,735** | **13,898** | **9,372** | **2,087** |
|  | ⏱️ Avg Latency | 5.37ms | 7.60ms | 10.41ms | 47.68ms |
|  | 📉 Max Latency | 16.98ms | 185.47ms | 31.57ms | 93.91ms |
|  | 📦 Transfer | 2.16 MB/s | 1.96 MB/s | 1.48 MB/s | 0.29 MB/s |
|  | 🔥 CPU Usage | 96% | 97% | 389% | 215% |
|  | 🧠 RAM Usage | 24.3 MB | 649.8 MB | 159.7 MB | 232.4 MB |
| | | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | **12,919** | 🥇 **17,215** | **9,071** | **2,039** |
|  | ⏱️ Avg Latency | 7.78ms | 6.27ms | 10.99ms | 48.74ms |
|  | 📉 Max Latency | 32.49ms | 177.28ms | 34.52ms | 125.64ms |
|  | 📦 Transfer | 1.55 MB/s | 1.86 MB/s | 1.41 MB/s | 0.28 MB/s |
|  | 🔥 CPU Usage | 96% | 97% | 390% | 225% |
|  | 🧠 RAM Usage | 24.6 MB | 1418.5 MB | 159.8 MB | 233.4 MB |
| | | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | **11,958** | 🥇 **16,004** | **8,090** | **1,968** |
|  | ⏱️ Avg Latency | 8.40ms | 8.06ms | 12.52ms | 50.43ms |
|  | 📉 Max Latency | 31.62ms | 293.26ms | 58.95ms | 100.86ms |
|  | 📦 Transfer | 1.40 MB/s | 2.26 MB/s | 1.23 MB/s | 0.26 MB/s |
|  | 🔥 CPU Usage | 96% | 97% | 387% | 240% |
|  | 🧠 RAM Usage | 24.7 MB | 2159.7 MB | 160.0 MB | 234.6 MB |
| | | --- | --- | --- | --- |

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```