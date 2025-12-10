# BustAPI Benchmark

**Version:** 0.3.1 (Highly Optimized)
**Date:** 2025-12-10

## Methodology

- **Tool:** wrk
- **Command:** `wrk -d 10s -c 100 http://127.0.0.1:5000/`
- **Environment:** Local Dev (Release Build + Optimized Python Path)
- **Configuration:** `workers=2` (Optimal for GIL balance)
- **Runs:** 5 passes, averaged.

## Results

| Metric  | Old Benchmark | Previous Optimization | **Final Result** | Improvement       |
| :------ | :------------ | :-------------------- | :--------------- | :---------------- |
| **RPS** | 13,719        | 19,540                | **24,849**       | **+81%** (vs Old) |

## Detailed Runs (Final)

| Run         | Requests/sec  |
| :---------- | :------------ |
| Run 1       | 29,548.52     |
| Run 2       | 22,752.84     |
| Run 3       | 24,053.13     |
| Run 4       | 23,588.68     |
| Run 5       | 24,299.84     |
| **Average** | **24,848.60** |
| **Peak**    | **29,548.52** |

## Optimization Techniques Implemented

1.  **Fast Path Execution**: Wrappers now detect empty Middleware/Session chains and perform early exits.
2.  **Response Object Bypass**: For simple types (`str`, `bytes`, `dict`), we bypass `Response` object creation and return raw tuples to Rust, eliminating Python object overhead.
3.  **Static Route Optimization**: Static paths (no `<param>`) skip the regex-based parameter extraction step.
4.  **Worker Tuning**: Tuned Actix `workers` to `2` to balance IO throughput with Python GIL contention.
