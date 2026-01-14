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
| **`/`** | 🚀 RPS | 🥇 **89,786** | **12,072** | **5,208** | **15,432** | **87,808** | **21,724** | **21,123** | **5,638** | **59,280** |
|  | ⏱️ Avg Latency | 1.23ms | 9.82ms | 19.04ms | 6.60ms | 1.15ms | 4.48ms | 4.64ms | 17.49ms | 1.84ms |
|  | 📉 Max Latency | 18.87ms | 310.66ms | 77.03ms | 56.57ms | 19.54ms | 22.83ms | 20.56ms | 46.81ms | 67.54ms |
|  | 📦 Transfer | 11.05 MB/s | 1.70 MB/s | 0.82 MB/s | 2.16 MB/s | 9.80 MB/s | 3.27 MB/s | 3.34 MB/s | 0.99 MB/s | 8.31 MB/s |
|  | 🔥 CPU Usage | 359% | 97% | 374% | 406% | 386% | 383% | 384% | 381% | 384% |
|  | 🧠 RAM Usage | 163.7 MB | 346.3 MB | 159.8 MB | 253.9 MB | 243.1 MB | 148.1 MB | 126.1 MB | 188.0 MB | 218.8 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **100,779** | **11,251** | **5,854** | **13,615** | **82,223** | **15,319** | **14,624** | **5,273** | **53,325** |
|  | ⏱️ Avg Latency | 1.05ms | 10.08ms | 17.05ms | 7.62ms | 1.29ms | 6.46ms | 6.63ms | 18.72ms | 1.90ms |
|  | 📉 Max Latency | 14.52ms | 245.28ms | 63.50ms | 79.79ms | 42.19ms | 27.54ms | 28.25ms | 33.26ms | 27.56ms |
|  | 📦 Transfer | 12.01 MB/s | 1.21 MB/s | 0.91 MB/s | 1.84 MB/s | 8.78 MB/s | 2.38 MB/s | 2.27 MB/s | 0.92 MB/s | 7.22 MB/s |
|  | 🔥 CPU Usage | 370% | 96% | 373% | 402% | 385% | 380% | 384% | 379% | 385% |
|  | 🧠 RAM Usage | 163.2 MB | 642.6 MB | 159.8 MB | 255.2 MB | 243.2 MB | 148.3 MB | 126.4 MB | 188.0 MB | 219.4 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | 🥇 **72,014** | **10,783** | **6,739** | **12,130** | **52,002** | **14,274** | **14,138** | **4,598** | **40,418** |
|  | ⏱️ Avg Latency | 1.47ms | 29.38ms | 14.74ms | 8.35ms | 2.03ms | 6.84ms | 6.94ms | 21.60ms | 2.70ms |
|  | 📉 Max Latency | 12.75ms | 766.92ms | 37.98ms | 70.47ms | 57.46ms | 22.89ms | 16.26ms | 70.32ms | 85.05ms |
|  | 📦 Transfer | 8.38 MB/s | 1.52 MB/s | 1.03 MB/s | 1.61 MB/s | 5.41 MB/s | 2.18 MB/s | 2.16 MB/s | 0.78 MB/s | 5.36 MB/s |
|  | 🔥 CPU Usage | 381% | 96% | 383% | 400% | 386% | 380% | 384% | 370% | 474% |
|  | 🧠 RAM Usage | 165.1 MB | 933.3 MB | 159.8 MB | 256.3 MB | 243.2 MB | 148.4 MB | 126.7 MB | 188.0 MB | 220.0 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## 📊 Performance Comparison
![RPS Comparison](rps_comparison.png)

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```