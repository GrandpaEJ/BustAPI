# 🚀 Web Framework Benchmark Results

**Date:** 2025-12-09
**Tool:** `benchmarks/run_comparison_auto.py`
**Config:** 4 threads, 100 connections, 5s duration, **NO LOGGING**

## 📊 Summary (Requests/sec)

| Endpoint                    | BustAPI    | Catzilla | Flask | FastAPI |
| --------------------------- | ---------- | -------- | ----- | ------- |
| **Plain Text (`/`)**        | **18,408** | 9,666    | 3,633 | 2,211   |
| **JSON (`/json`)**          | **13,109** | 10,277   | 3,570 | 2,164   |
| **Path Param (`/user/10`)** | **13,641** | 6,572    | 3,659 | 2,083   |

## 🏆 Performance Highlights

### BustAPI vs Catzilla

- **BustAPI** is **1.3x - 2x faster** than Catzilla.
- Catzilla shows strong performance on JSON (~10k RPS).

### BustAPI vs Flask

- **BustAPI** is **~4x - 5x faster** than Flask.

### Side Note: FastAPI

- FastAPI results (~2k RPS) seem lower than expected for this framework, suggesting potential environment overheads or configuration limits in this specific test setup.

## 🏃 How to Run

```bash
# Clean ports
fuser -k 8000/tcp

# Run automated benchmark
uv run --extra benchmarks benchmarks/run_comparison_auto.py
```
