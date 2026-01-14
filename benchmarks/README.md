# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2026-01-15 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-37-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.13.11`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI (4w) | Catzilla (4w) | Flask (4w) | FastAPI (4w) | Sanic (4w) | Falcon (4w) | Bottle (4w) | Django (4w) | BlackSheep (4w) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | **47,439** | **6,426** | **2,746** | **6,769** | **36,176** | **8,185** | **5,236** | **3,461** | 🥇 **50,746** |
|  | ⏱️ Avg Latency | 2.34ms | 18.96ms | 35.61ms | 15.17ms | 2.75ms | 11.90ms | 18.57ms | 29.49ms | 2.08ms |
|  | 📉 Max Latency | 52.33ms | 466.42ms | 80.33ms | 107.75ms | 30.92ms | 61.82ms | 66.75ms | 124.85ms | 33.60ms |
|  | 📦 Transfer | 5.84 MB/s | 0.91 MB/s | 0.43 MB/s | 0.95 MB/s | 4.04 MB/s | 1.23 MB/s | 0.83 MB/s | 0.61 MB/s | 7.11 MB/s |
|  | 🔥 CPU Usage | 340% | 93% | 346% | 350% | 374% | 353% | 319% | 325% | 380% |
|  | 🧠 RAM Usage | 111.3 MB | 190.3 MB | 159.5 MB | 252.9 MB | 243.2 MB | 147.8 MB | 126.2 MB | 187.8 MB | 218.1 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **50,974** | **7,892** | **2,933** | **4,972** | **28,835** | **12,249** | **4,721** | **1,891** | **45,903** |
|  | ⏱️ Avg Latency | 1.99ms | 22.16ms | 33.42ms | 20.77ms | 3.43ms | 8.00ms | 20.50ms | 51.62ms | 2.22ms |
|  | 📉 Max Latency | 23.26ms | 577.93ms | 70.97ms | 99.12ms | 28.93ms | 41.62ms | 65.43ms | 105.79ms | 16.34ms |
|  | 📦 Transfer | 6.08 MB/s | 0.85 MB/s | 0.46 MB/s | 0.67 MB/s | 3.08 MB/s | 1.90 MB/s | 0.73 MB/s | 0.33 MB/s | 6.22 MB/s |
|  | 🔥 CPU Usage | 358% | 96% | 364% | 323% | 372% | 350% | 316% | 298% | 382% |
|  | 🧠 RAM Usage | 111.6 MB | 407.4 MB | 159.6 MB | 254.0 MB | 243.3 MB | 148.1 MB | 126.4 MB | 188.1 MB | 218.8 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | **30,467** | **6,508** | **2,872** | **3,207** | **27,805** | **14,720** | **4,977** | **3,927** | 🥇 **48,081** |
|  | ⏱️ Avg Latency | 3.36ms | 18.81ms | 34.22ms | 30.82ms | 3.58ms | 6.68ms | 19.19ms | 25.13ms | 2.10ms |
|  | 📉 Max Latency | 39.35ms | 487.96ms | 108.00ms | 75.88ms | 31.55ms | 27.71ms | 57.06ms | 54.34ms | 18.58ms |
|  | 📦 Transfer | 3.54 MB/s | 0.92 MB/s | 0.44 MB/s | 0.43 MB/s | 2.89 MB/s | 2.25 MB/s | 0.76 MB/s | 0.67 MB/s | 6.37 MB/s |
|  | 🔥 CPU Usage | 360% | 94% | 362% | 318% | 367% | 374% | 329% | 363% | 384% |
|  | 🧠 RAM Usage | 113.4 MB | 580.2 MB | 159.6 MB | 254.6 MB | 243.3 MB | 148.1 MB | 126.7 MB | 188.1 MB | 219.3 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## 📊 Performance Comparison
![RPS Comparison](rps_comparison.png)

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```