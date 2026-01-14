# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2026-01-15 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.14.0-37-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.13.11`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI (4w) | Catzilla (4w) | Flask (4w) | FastAPI (4w) | Robyn (4w) | Sanic (4w) | Falcon (4w) | Bottle (4w) | Django (4w) | BlackSheep (4w) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | **25,422** | **13,605** | **8,021** | **11,544** | **10,372** | 🥇 **72,774** | **16,573** | **15,504** | **3,975** | **52,141** |
|  | ⏱️ Avg Latency | 3.94ms | 7.99ms | 12.35ms | 8.79ms | 9.63ms | 1.37ms | 6.04ms | 6.28ms | 25.00ms | 1.94ms |
|  | 📉 Max Latency | 17.26ms | 202.30ms | 33.24ms | 63.71ms | 29.91ms | 14.27ms | 51.29ms | 25.85ms | 95.72ms | 27.57ms |
|  | 📦 Transfer | 3.13 MB/s | 1.92 MB/s | 1.27 MB/s | 1.62 MB/s | 1.14 MB/s | 8.12 MB/s | 2.50 MB/s | 2.45 MB/s | 0.70 MB/s | 7.31 MB/s |
|  | 🔥 CPU Usage | 185% | 96% | 385% | 393% | 95% | 382% | 377% | 377% | 357% | 382% |
|  | 🧠 RAM Usage | 59.5 MB | 387.8 MB | 159.6 MB | 254.1 MB | 34.9 MB | 243.2 MB | 148.0 MB | 125.7 MB | 188.0 MB | 218.3 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | **25,763** | **14,063** | **7,681** | **9,729** | **10,070** | 🥇 **55,332** | **12,267** | **14,168** | **3,804** | **37,091** |
|  | ⏱️ Avg Latency | 3.91ms | 8.68ms | 12.91ms | 10.32ms | 9.99ms | 2.05ms | 7.96ms | 7.01ms | 25.66ms | 3.15ms |
|  | 📉 Max Latency | 20.66ms | 254.78ms | 35.23ms | 44.86ms | 30.09ms | 82.04ms | 41.08ms | 38.54ms | 80.60ms | 88.86ms |
|  | 📦 Transfer | 3.07 MB/s | 1.52 MB/s | 1.19 MB/s | 1.32 MB/s | 1.14 MB/s | 5.91 MB/s | 1.91 MB/s | 2.20 MB/s | 0.66 MB/s | 5.02 MB/s |
|  | 🔥 CPU Usage | 187% | 96% | 517% | 384% | 96% | 380% | 366% | 379% | 355% | 367% |
|  | 🧠 RAM Usage | 59.0 MB | 761.4 MB | 159.6 MB | 255.4 MB | 35.2 MB | 243.3 MB | 148.2 MB | 126.0 MB | 188.2 MB | 218.9 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | **16,606** | **13,112** | **6,769** | **8,821** | **9,344** | 🥇 **63,029** | **14,133** | **13,112** | **4,213** | **46,519** |
|  | ⏱️ Avg Latency | 7.35ms | 10.40ms | 14.65ms | 11.19ms | 10.68ms | 1.58ms | 6.96ms | 7.59ms | 23.36ms | 2.20ms |
|  | 📉 Max Latency | 38.10ms | 325.73ms | 29.73ms | 50.92ms | 28.76ms | 16.16ms | 41.19ms | 35.41ms | 51.63ms | 14.86ms |
|  | 📦 Transfer | 1.93 MB/s | 1.85 MB/s | 1.03 MB/s | 1.17 MB/s | 1.03 MB/s | 6.55 MB/s | 2.16 MB/s | 2.00 MB/s | 0.72 MB/s | 6.17 MB/s |
|  | 🔥 CPU Usage | 146% | 96% | 383% | 387% | 96% | 384% | 367% | 471% | 371% | 383% |
|  | 🧠 RAM Usage | 52.3 MB | 1118.6 MB | 159.6 MB | 256.1 MB | 35.2 MB | 243.3 MB | 148.3 MB | 126.3 MB | 188.3 MB | 219.5 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## 📊 Performance Comparison
![RPS Comparison](rps_comparison.png)

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```