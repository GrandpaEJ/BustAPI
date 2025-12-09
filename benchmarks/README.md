# 🚀 Web Framework Benchmark Results

**Date:** 2025-12-09
**Tool:** `benchmarks/run_comparison_auto.py`
**Config:** 4 threads, 100 connections, 5s duration

## 📊 Summary (Requests/sec)

| Endpoint | Metric | BustAPI | Flask | FastAPI | Catzilla |
|--------|------|-------|-----|-------|--------|
| **/** | Req/Sec | **18,428** | 4,118 | 2,158 | 10,826 |
|  | CPU % | 154.0% | 375.6% | 209.1% | 95.2% |
|  | RAM (MB) | 53.6 | 181.2 | 257.5 | 539.5 |
| | | --- | --- | --- | --- |
| **/json** | Req/Sec | **14,331** | 4,092 | 1,874 | 9,176 |
|  | CPU % | 147.6% | 380.6% | 206.1% | 97.7% |
|  | RAM (MB) | 54.0 | 181.4 | 258.3 | 941.9 |
| | | --- | --- | --- | --- |
| **/user/10** | Req/Sec | **13,287** | 3,839 | 2,046 | 8,283 |
|  | CPU % | 145.9% | 380.9% | 214.0% | 97.6% |
|  | RAM (MB) | 54.0 | 181.3 | 259.7 | 1316.6 |
| | | --- | --- | --- | --- |

## 🏃 How to Run

```bash
# Clean ports
fuser -k 8000/tcp

# Run automated benchmark
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```