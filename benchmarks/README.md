# 🚀 Web Framework Benchmark Results

**Date:** 2025-12-09
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
| **/** | Req/Sec | **19,678** | 5,534 | 2,174 | 9,809 |
|  | CPU % | 160.3% | 374.4% | 170.1% | 97.6% |
|  | RAM (MB) | 53.5 | 181.0 | 257.3 | 488.5 |
| | | --- | --- | --- | --- |
| **/json** | Req/Sec | **18,551** | 4,980 | 2,212 | 9,986 |
|  | CPU % | 151.4% | 368.9% | 330.8% | 97.9% |
|  | RAM (MB) | 53.9 | 181.1 | 258.3 | 936.3 |
| | | --- | --- | --- | --- |
| **/user/10** | Req/Sec | **14,669** | 5,615 | 2,044 | 8,391 |
|  | CPU % | 142.2% | 387.6% | 207.7% | 93.1% |
|  | RAM (MB) | 53.9 | 181.0 | 259.6 | 1316.9 |
| | | --- | --- | --- | --- |

## 🏃 How to Run

```bash
# Clean ports
fuser -k 8000/tcp

# Run automated benchmark
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```