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
| **`/`** | 🚀 RPS | 🥇 **34,106** | **15,005** | **9,743** | **2,224** |
|  | ⏱️ Avg Latency | 2.93ms | 6.87ms | 10.18ms | 44.70ms |
|  | 📉 Max Latency | 9.24ms | 178.55ms | 26.44ms | 87.84ms |
|  | 📦 Transfer | 4.20 MB/s | 2.12 MB/s | 1.54 MB/s | 0.31 MB/s |
|  | 🔥 CPU Usage | 97% | 98% | 391% | 315% |
|  | 🧠 RAM Usage | 39.4 MB | 695.8 MB | 159.0 MB | 230.9 MB |
| | | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **34,569** | **14,736** | **9,177** | **2,177** |
|  | ⏱️ Avg Latency | 2.89ms | 6.95ms | 10.70ms | 45.64ms |
|  | 📉 Max Latency | 6.27ms | 131.23ms | 25.26ms | 118.00ms |
|  | 📦 Transfer | 4.12 MB/s | 1.59 MB/s | 1.43 MB/s | 0.30 MB/s |
|  | 🔥 CPU Usage | 97% | 98% | 390% | 150% |
|  | 🧠 RAM Usage | 39.0 MB | 1359.5 MB | 159.0 MB | 232.7 MB |
| | | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **18,476** | **11,664** | **7,210** | **2,160** |
|  | ⏱️ Avg Latency | 5.42ms | 8.98ms | 13.75ms | 46.25ms |
|  | 📉 Max Latency | 27.99ms | 215.66ms | 30.61ms | 126.70ms |
|  | 📦 Transfer | 2.17 MB/s | 1.65 MB/s | 1.10 MB/s | 0.29 MB/s |
|  | 🔥 CPU Usage | 97% | 98% | 391% | 133% |
|  | 🧠 RAM Usage | 38.9 MB | 1892.6 MB | 159.3 MB | 234.0 MB |
| | | --- | --- | --- | --- |

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```