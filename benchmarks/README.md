# ⚡ Ultimate Web Framework Benchmark

> **Date:** 2026-02-11 | **Tool:** `wrk`

## 🖥️ System Spec
- **OS:** `Linux 6.17.0-14-generic`
- **CPU:** `Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz` (8 Cores)
- **RAM:** `15.4 GB`
- **Python:** `3.13.11`

## 🏆 Throughput (Requests/sec)

| Endpoint | Metrics | BustAPI (4w) | Flask (4w) | FastAPI (4w) | Sanic (4w) | Falcon (4w) | Bottle (4w) | Django (4w) | BlackSheep (4w) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`/`** | 🚀 RPS | 🥇 **56,680** | **3,190** | **6,682** | **44,171** | **10,500** | **8,704** | **3,065** | **31,372** |
|  | ⏱️ Avg Latency | 1.79ms | 30.87ms | 15.43ms | 2.44ms | 9.23ms | 11.14ms | 32.01ms | 3.30ms |
|  | 📉 Max Latency | 12.62ms | 71.00ms | 116.35ms | 74.58ms | 38.88ms | 44.49ms | 64.05ms | 38.21ms |
|  | 📦 Transfer | 6.97 MB/s | 0.51 MB/s | 0.94 MB/s | 4.93 MB/s | 1.58 MB/s | 1.38 MB/s | 0.54 MB/s | 4.40 MB/s |
|  | 🔥 CPU Usage | 361% | 353% | 364% | 378% | 344% | 348% | 356% | 366% |
|  | 🧠 RAM Usage | 158.7 MB | 157.2 MB | 248.5 MB | 239.4 MB | 147.5 MB | 125.0 MB | 189.5 MB | 216.7 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/json`** | 🚀 RPS | 🥇 **43,525** | **2,861** | **6,596** | **38,670** | **9,962** | **4,315** | **2,881** | **29,151** |
|  | ⏱️ Avg Latency | 2.42ms | 34.13ms | 15.53ms | 2.60ms | 9.54ms | 21.92ms | 33.80ms | 3.38ms |
|  | 📉 Max Latency | 50.97ms | 87.76ms | 110.67ms | 21.32ms | 31.26ms | 70.79ms | 69.59ms | 34.10ms |
|  | 📦 Transfer | 5.19 MB/s | 0.44 MB/s | 0.89 MB/s | 4.13 MB/s | 1.55 MB/s | 0.67 MB/s | 0.50 MB/s | 3.95 MB/s |
|  | 🔥 CPU Usage | 338% | 346% | 363% | 377% | 364% | 279% | 348% | 638% |
|  | 🧠 RAM Usage | 158.3 MB | 157.3 MB | 249.5 MB | 239.5 MB | 147.7 MB | 125.3 MB | 189.5 MB | 217.4 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- |
| **`/user/10`** | 🚀 RPS | **29,792** | **2,914** | **5,208** | 🥇 **38,681** | **9,938** | **4,506** | **2,495** | **29,072** |
|  | ⏱️ Avg Latency | 3.50ms | 33.59ms | 20.14ms | 2.57ms | 9.59ms | 21.18ms | 39.46ms | 3.45ms |
|  | 📉 Max Latency | 21.83ms | 111.86ms | 111.20ms | 17.68ms | 24.16ms | 122.56ms | 92.58ms | 36.46ms |
|  | 📦 Transfer | 3.47 MB/s | 0.44 MB/s | 0.69 MB/s | 4.02 MB/s | 1.52 MB/s | 0.69 MB/s | 0.42 MB/s | 3.85 MB/s |
|  | 🔥 CPU Usage | 312% | 339% | 353% | 384% | 635% | 293% | 319% | 380% |
|  | 🧠 RAM Usage | 160.6 MB | 157.3 MB | 250.8 MB | 239.5 MB | 147.7 MB | 125.6 MB | 189.5 MB | 217.9 MB |
| | | --- | --- | --- | --- | --- | --- | --- | --- |

## 📊 Performance Comparison
![RPS Comparison](rps_comparison.png)

## ⚙️ How to Reproduce
```bash
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```