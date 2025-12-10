# 🚀 Web Framework Benchmark Results

**Date:** 2025-12-10
**Tool:** `benchmarks/run_comparison_auto.py`

## 💻 Test Environment
- **OS:** Linux 6.14.0-36-generic
- **CPU:** Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz (8 Cores)
- **RAM:** 15.4 GB
- **Python:** 3.13.11

**Config:** 4 threads, 100 connections, 5s duration

## 📊 Summary (Requests/sec)

| Endpoint | Metric | BustAPI | Flask | FastAPI | Catzilla |
|--------|------|-------|-----|-------|--------|
| **/** | Req/Sec | **19,635** | 3,526 | N/A | 8,851 |
|  | CPU % | 162.3% | 364.6% | N/A | 97.7% |
|  | RAM (MB) | 57.1 | 182.9 | N/A | 453.7 |
| | | --- | --- | --- | --- |
| **/json** | Req/Sec | **12,784** | 4,868 | N/A | 9,350 |
|  | CPU % | 144.5% | 375.0% | N/A | 97.8% |
|  | RAM (MB) | 57.4 | 183.0 | N/A | 862.8 |
| | | --- | --- | --- | --- |
| **/user/10** | Req/Sec | **11,541** | 4,396 | N/A | 8,520 |
|  | CPU % | 147.5% | 382.1% | N/A | 97.8% |
|  | RAM (MB) | 57.6 | 182.8 | N/A | 1252.9 |
| | | --- | --- | --- | --- |

## 🏃 How to Run

```bash
# Clean ports
fuser -k 8000/tcp

# Run automated benchmark
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```