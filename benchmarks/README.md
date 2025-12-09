# 🚀 Web Framework Benchmark Results

**Date:** 2025-12-09
**Tool:** `benchmarks/run_comparison_auto.py`
**Config:** 4 threads, 100 connections, 5s duration

## 📊 Summary (Requests/sec)

| Endpoint     | Metric   | BustAPI    | Flask | FastAPI | Catzilla |
| ------------ | -------- | ---------- | ----- | ------- | -------- |
| **/**        | Req/Sec  | **16,666** | 4,050 | 2,149   | 8,261    |
|              | RAM (MB) | 53.7       | 181.0 | 257.9   | 425.4    |
|              |          | ---        | ---   | ---     | ---      |
| **/json**    | Req/Sec  | **12,864** | 5,986 | 2,153   | 8,792    |
|              | RAM (MB) | 53.9       | 181.2 | 259.4   | 817.7    |
|              |          | ---        | ---   | ---     | ---      |
| **/user/10** | Req/Sec  | **11,852** | 5,114 | 2,045   | 7,808    |
|              | RAM (MB) | 53.9       | 181.1 | 260.1   | 1170.9   |
|              |          | ---        | ---   | ---     | ---      |

## 🏃 How to Run

```bash
# Clean ports
fuser -k 8000/tcp

# Run automated benchmark
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```
