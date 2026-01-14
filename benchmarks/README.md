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
| **`/`** | 🚀 RPS | 🥇 **97,376** | **7,398** | **3,521** | **6,107** | **41,327** | **16,539** | **9,159** | **2,732** | **28,662** |
|  | ⏱️ Avg Latency | 1.04ms | 16.51ms | 28.03ms | 17.27ms | 2.42ms | 5.85ms | 10.63ms | 36.05ms | 3.49ms |
|  | 📉 Max Latency | 8.58ms | 441.96ms | 50.02ms | 167.99ms | 28.67ms | 17.60ms | 18.66ms | 53.24ms | 30.19ms |
|  | 📦 Transfer | 11.98 MB/s | 1.04 MB/s | 0.56 MB/s | 0.86 MB/s | 4.61 MB/s | 2.49 MB/s | 1.45 MB/s | 0.48 MB/s | 4.02 MB/s |
|  | 🔥 CPU Usage | 374% | 95% | 366% | 356% | 381% | 374% | 378% | 364% | 379% |
|  | 🧠 RAM Usage | 152.1 MB | 219.1 MB | 159.4 MB | 254.1 MB | 242.9 MB | 148.1 MB | 125.9 MB | 187.7 MB | 217.1 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **93,770** | **8,908** | **3,592** | **7,365** | **33,207** | **19,068** | **8,203** | **2,530** | **27,111** |
|  | ⏱️ Avg Latency | 1.07ms | 16.77ms | 27.46ms | 13.98ms | 3.00ms | 5.14ms | 11.96ms | 38.77ms | 3.69ms |
|  | 📉 Max Latency | 7.54ms | 462.10ms | 64.29ms | 80.20ms | 23.70ms | 24.01ms | 41.49ms | 59.45ms | 28.40ms |
|  | 📦 Transfer | 11.18 MB/s | 0.96 MB/s | 0.56 MB/s | 1.00 MB/s | 3.55 MB/s | 2.96 MB/s | 1.28 MB/s | 0.44 MB/s | 3.67 MB/s |
|  | 🔥 CPU Usage | 376% | 97% | 372% | 372% | 381% | 381% | 378% | 358% | 384% |
|  | 🧠 RAM Usage | 152.1 MB | 465.4 MB | 159.4 MB | 255.7 MB | 243.0 MB | 148.3 MB | 125.9 MB | 188.0 MB | 217.7 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **46,464** | **7,152** | **3,200** | **5,601** | **33,837** | **8,306** | **7,719** | **1,981** | **23,839** |
|  | ⏱️ Avg Latency | 2.24ms | 15.06ms | 30.63ms | 18.00ms | 2.99ms | 11.49ms | 12.70ms | 49.53ms | 4.40ms |
|  | 📉 Max Latency | 22.83ms | 310.61ms | 74.49ms | 82.01ms | 37.83ms | 101.45ms | 44.18ms | 78.79ms | 75.97ms |
|  | 📦 Transfer | 5.41 MB/s | 1.01 MB/s | 0.49 MB/s | 0.74 MB/s | 3.52 MB/s | 1.27 MB/s | 1.18 MB/s | 0.34 MB/s | 3.16 MB/s |
|  | 🔥 CPU Usage | 354% | 96% | 365% | 350% | 375% | 351% | 378% | 308% | 463% |
|  | 🧠 RAM Usage | 153.7 MB | 649.6 MB | 159.5 MB | 256.6 MB | 243.0 MB | 148.4 MB | 126.2 MB | 188.0 MB | 218.1 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## 📊 Performance Comparison
![RPS Comparison](rps_comparison.png)

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```