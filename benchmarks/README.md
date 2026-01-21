# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2026-01-22 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-37-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.13.11`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI (4w) | Catzilla (4w) | Flask (4w) | FastAPI (4w) | Sanic (4w) | Falcon (4w) | Bottle (4w) | Django (4w) | BlackSheep (4w) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | 🥇 **111,348** | **15,662** | **5,455** | **15,004** | **59,119** | **14,259** | **14,763** | **5,386** | **55,899** |
|  | ⏱️ Avg Latency | 0.90ms | 7.19ms | 17.80ms | 6.93ms | 1.68ms | 6.68ms | 6.59ms | 18.60ms | 1.81ms |
|  | 📉 Max Latency | 7.53ms | 208.01ms | 48.79ms | 74.74ms | 16.08ms | 19.86ms | 24.03ms | 74.42ms | 28.45ms |
|  | 📦 Transfer | 13.70 MB/s | 2.21 MB/s | 0.86 MB/s | 2.10 MB/s | 6.60 MB/s | 2.15 MB/s | 2.34 MB/s | 0.95 MB/s | 7.84 MB/s |
|  | 🔥 CPU Usage | 380% | 96% | 373% | 405% | 382% | 371% | 374% | 377% | 385% |
|  | 🧠 RAM Usage | 160.8 MB | 437.9 MB | 159.7 MB | 253.9 MB | 243.2 MB | 147.7 MB | 126.0 MB | 187.9 MB | 218.6 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **110,903** | **16,935** | **8,976** | **12,180** | **60,566** | **13,292** | **16,148** | **5,025** | **49,529** |
|  | ⏱️ Avg Latency | 0.97ms | 8.93ms | 10.84ms | 8.49ms | 1.72ms | 7.22ms | 6.10ms | 19.67ms | 2.19ms |
|  | 📉 Max Latency | 20.29ms | 301.74ms | 31.05ms | 80.07ms | 45.85ms | 20.94ms | 26.11ms | 41.03ms | 79.80ms |
|  | 📦 Transfer | 13.22 MB/s | 1.82 MB/s | 1.40 MB/s | 1.65 MB/s | 6.47 MB/s | 2.07 MB/s | 2.51 MB/s | 0.87 MB/s | 6.71 MB/s |
|  | 🔥 CPU Usage | 379% | 97% | 386% | 396% | 384% | 645% | 377% | 380% | 385% |
|  | 🧠 RAM Usage | 160.0 MB | 891.7 MB | 159.8 MB | 255.4 MB | 243.3 MB | 148.0 MB | 126.3 MB | 188.1 MB | 219.2 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **90,033** | **11,940** | **9,125** | **8,503** | **57,390** | **16,153** | **12,246** | **4,703** | **49,896** |
|  | ⏱️ Avg Latency | 1.11ms | 8.89ms | 10.61ms | 11.77ms | 1.72ms | 5.91ms | 8.14ms | 21.07ms | 2.13ms |
|  | 📉 Max Latency | 4.63ms | 199.34ms | 24.78ms | 47.64ms | 17.85ms | 20.25ms | 57.35ms | 70.04ms | 66.02ms |
|  | 📦 Transfer | 10.48 MB/s | 1.69 MB/s | 1.39 MB/s | 1.13 MB/s | 5.97 MB/s | 2.46 MB/s | 1.87 MB/s | 0.80 MB/s | 6.61 MB/s |
|  | 🔥 CPU Usage | 381% | 96% | 385% | 383% | 385% | 379% | 377% | 364% | 385% |
|  | 🧠 RAM Usage | 157.9 MB | 1211.4 MB | 159.8 MB | 256.6 MB | 243.4 MB | 148.0 MB | 126.6 MB | 188.1 MB | 219.8 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## 📊 Performance Comparison
![RPS Comparison](rps_comparison.png)

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```