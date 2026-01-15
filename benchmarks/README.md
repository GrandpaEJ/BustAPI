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
| **`/`** | 🚀 RPS | 🥇 **105,012** | **13,825** | **7,806** | **12,723** | **76,469** | **20,294** | **20,100** | **4,913** | **41,176** |
|  | ⏱️ Avg Latency | 1.00ms | 7.57ms | 12.69ms | 7.95ms | 1.32ms | 4.72ms | 4.86ms | 20.25ms | 2.48ms |
|  | 📉 Max Latency | 22.09ms | 159.06ms | 34.53ms | 41.40ms | 9.84ms | 20.98ms | 10.19ms | 61.76ms | 33.85ms |
|  | 📦 Transfer | 12.92 MB/s | 1.95 MB/s | 1.24 MB/s | 1.78 MB/s | 8.53 MB/s | 3.06 MB/s | 3.18 MB/s | 0.86 MB/s | 5.77 MB/s |
|  | 🔥 CPU Usage | 376% | 96% | 384% | 393% | 385% | 380% | 381% | 365% | 374% |
|  | 🧠 RAM Usage | 105.7 MB | 392.8 MB | 160.0 MB | 253.9 MB | 243.4 MB | 148.2 MB | 126.0 MB | 188.4 MB | 218.9 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **99,142** | **13,481** | **7,033** | **13,873** | **69,503** | **14,681** | **13,398** | **4,682** | **31,538** |
|  | ⏱️ Avg Latency | 1.05ms | 13.61ms | 14.17ms | 7.09ms | 1.50ms | 6.54ms | 7.35ms | 21.79ms | 3.19ms |
|  | 📉 Max Latency | 11.56ms | 443.81ms | 54.62ms | 27.00ms | 49.68ms | 17.81ms | 28.02ms | 88.41ms | 27.99ms |
|  | 📦 Transfer | 11.82 MB/s | 1.45 MB/s | 1.09 MB/s | 1.88 MB/s | 7.42 MB/s | 2.28 MB/s | 2.08 MB/s | 0.81 MB/s | 4.27 MB/s |
|  | 🔥 CPU Usage | 378% | 96% | 383% | 405% | 386% | 377% | 377% | 354% | 379% |
|  | 🧠 RAM Usage | 105.7 MB | 745.1 MB | 160.1 MB | 255.2 MB | 243.5 MB | 148.2 MB | 126.2 MB | 188.4 MB | 219.4 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **64,669** | **14,297** | **8,424** | **9,962** | **56,016** | **13,902** | **12,682** | **4,742** | **27,598** |
|  | ⏱️ Avg Latency | 1.55ms | 10.47ms | 11.68ms | 10.34ms | 1.83ms | 7.08ms | 7.91ms | 20.79ms | 3.63ms |
|  | 📉 Max Latency | 21.28ms | 329.88ms | 26.61ms | 97.68ms | 22.96ms | 30.56ms | 37.26ms | 39.41ms | 29.17ms |
|  | 📦 Transfer | 7.52 MB/s | 2.02 MB/s | 1.29 MB/s | 1.32 MB/s | 5.82 MB/s | 2.12 MB/s | 1.94 MB/s | 0.81 MB/s | 3.66 MB/s |
|  | 🔥 CPU Usage | 378% | 96% | 382% | 396% | 739% | 380% | 381% | 371% | 374% |
|  | 🧠 RAM Usage | 107.7 MB | 1151.9 MB | 160.1 MB | 256.1 MB | 243.5 MB | 148.5 MB | 126.5 MB | 188.4 MB | 219.9 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## 📊 Performance Comparison
![RPS Comparison](rps_comparison.png)

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```