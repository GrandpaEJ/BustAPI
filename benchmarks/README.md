# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2026-01-20 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-37-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.13.11`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI (4w) | Catzilla (4w) | Flask (4w) | FastAPI (4w) | Sanic (4w) | Falcon (4w) | Bottle (4w) | Django (4w) | BlackSheep (4w) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | 🥇 **88,914** | **13,389** | **6,401** | **11,038** | **56,319** | **14,433** | **12,250** | **4,557** | **34,128** |
|  | ⏱️ Avg Latency | 1.16ms | 8.80ms | 15.44ms | 9.11ms | 1.86ms | 6.68ms | 7.93ms | 21.62ms | 2.99ms |
|  | 📉 Max Latency | 11.63ms | 256.67ms | 28.69ms | 47.14ms | 34.71ms | 23.22ms | 28.22ms | 38.97ms | 27.07ms |
|  | 📦 Transfer | 10.94 MB/s | 1.89 MB/s | 1.01 MB/s | 1.55 MB/s | 6.28 MB/s | 2.17 MB/s | 1.94 MB/s | 0.80 MB/s | 4.78 MB/s |
|  | 🔥 CPU Usage | 365% | 96% | 381% | 387% | 378% | 364% | 362% | 371% | 361% |
|  | 🧠 RAM Usage | 114.6 MB | 381.9 MB | 159.2 MB | 253.3 MB | 243.1 MB | 148.0 MB | 125.9 MB | 187.8 MB | 217.9 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **80,988** | **14,005** | **5,292** | **10,554** | **33,811** | **9,745** | **9,872** | **4,249** | **27,207** |
|  | ⏱️ Avg Latency | 1.24ms | 7.19ms | 18.59ms | 9.78ms | 2.99ms | 9.70ms | 9.80ms | 23.28ms | 3.76ms |
|  | 📉 Max Latency | 5.89ms | 145.99ms | 43.33ms | 88.63ms | 23.47ms | 19.75ms | 21.25ms | 56.94ms | 31.43ms |
|  | 📦 Transfer | 9.65 MB/s | 1.51 MB/s | 0.82 MB/s | 1.43 MB/s | 3.61 MB/s | 1.51 MB/s | 1.53 MB/s | 0.74 MB/s | 3.68 MB/s |
|  | 🔥 CPU Usage | 377% | 97% | 375% | 392% | 367% | 361% | 377% | 362% | 366% |
|  | 🧠 RAM Usage | 114.9 MB | 755.5 MB | 159.3 MB | 254.4 MB | 243.2 MB | 148.2 MB | 126.2 MB | 188.1 MB | 218.5 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **42,360** | **12,088** | **4,761** | **8,518** | **35,258** | **9,437** | **9,237** | **3,979** | **27,900** |
|  | ⏱️ Avg Latency | 2.33ms | 8.52ms | 20.76ms | 11.45ms | 2.81ms | 10.06ms | 10.44ms | 24.82ms | 3.59ms |
|  | 📉 Max Latency | 7.67ms | 160.98ms | 36.82ms | 38.17ms | 21.63ms | 25.92ms | 24.67ms | 51.21ms | 18.73ms |
|  | 📦 Transfer | 4.93 MB/s | 1.71 MB/s | 0.73 MB/s | 1.13 MB/s | 3.67 MB/s | 1.44 MB/s | 1.41 MB/s | 0.68 MB/s | 3.70 MB/s |
|  | 🔥 CPU Usage | 381% | 96% | 379% | 394% | 379% | 365% | 373% | 377% | 382% |
|  | 🧠 RAM Usage | 116.8 MB | 1089.5 MB | 159.3 MB | 255.4 MB | 243.2 MB | 148.3 MB | 126.5 MB | 188.1 MB | 219.1 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## 📊 Performance Comparison
![RPS Comparison](rps_comparison.png)

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```