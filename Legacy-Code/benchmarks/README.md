# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2026-01-27 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-37-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.13.11`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI (4w) | Flask (4w) | FastAPI (4w) | Sanic (4w) | Falcon (4w) | Bottle (4w) | Django (4w) | BlackSheep (4w) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | 🥇 **112,283** | **9,731** | **15,898** | **86,150** | **20,619** | **21,987** | **7,435** | **69,234** |
|  | ⏱️ Avg Latency | 0.91ms | 9.96ms | 6.96ms | 1.19ms | 4.60ms | 4.43ms | 13.35ms | 1.47ms |
|  | 📉 Max Latency | 16.48ms | 26.55ms | 99.00ms | 37.48ms | 18.05ms | 14.65ms | 44.27ms | 22.42ms |
|  | 📦 Transfer | 13.81 MB/s | 1.54 MB/s | 2.23 MB/s | 9.61 MB/s | 3.11 MB/s | 3.48 MB/s | 1.30 MB/s | 9.71 MB/s |
|  | 🔥 CPU Usage | 381% | 384% | 539% | 388% | 369% | 382% | 384% | 386% |
|  | 🧠 RAM Usage | 162.3 MB | 158.4 MB | 279.6 MB | 244.1 MB | 151.5 MB | 143.5 MB | 204.8 MB | 224.2 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **114,330** | **9,733** | **15,100** | **63,152** | **16,930** | **15,076** | **7,399** | **51,709** |
|  | ⏱️ Avg Latency | 0.87ms | 10.18ms | 6.48ms | 1.56ms | 5.90ms | 6.58ms | 13.09ms | 1.93ms |
|  | 📉 Max Latency | 4.59ms | 23.76ms | 29.11ms | 10.44ms | 27.68ms | 29.96ms | 29.74ms | 21.15ms |
|  | 📦 Transfer | 13.63 MB/s | 1.51 MB/s | 2.04 MB/s | 6.75 MB/s | 2.63 MB/s | 2.34 MB/s | 1.28 MB/s | 7.00 MB/s |
|  | 🔥 CPU Usage | 382% | 386% | 408% | 386% | 385% | 385% | 384% | 386% |
|  | 🧠 RAM Usage | 161.5 MB | 158.4 MB | 280.2 MB | 244.2 MB | 151.5 MB | 143.8 MB | 205.1 MB | 224.5 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **90,731** | **9,241** | **13,530** | **55,241** | **15,930** | **14,703** | **6,017** | **46,352** |
|  | ⏱️ Avg Latency | 1.07ms | 10.73ms | 7.38ms | 1.93ms | 6.14ms | 6.81ms | 16.09ms | 2.23ms |
|  | 📉 Max Latency | 4.80ms | 24.51ms | 26.36ms | 66.16ms | 13.37ms | 29.87ms | 23.86ms | 64.51ms |
|  | 📦 Transfer | 10.56 MB/s | 1.41 MB/s | 1.79 MB/s | 5.74 MB/s | 2.43 MB/s | 2.24 MB/s | 1.02 MB/s | 6.14 MB/s |
|  | 🔥 CPU Usage | 384% | 385% | 406% | 386% | 386% | 496% | 385% | 474% |
|  | 🧠 RAM Usage | 163.6 MB | 158.4 MB | 280.3 MB | 244.2 MB | 151.6 MB | 144.0 MB | 205.1 MB | 224.8 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- |

## 📊 Performance Comparison
![RPS Comparison](rps_comparison.png)

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```