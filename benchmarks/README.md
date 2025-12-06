# 🚀 Web Framework Benchmark Results

**Date:** 2025-12-06 16:41:52
**Config:** 15s duration, 4 threads, 100 connections

## 📊 Summary (Requests/sec)

| Endpoint | Flask | FastAPI | BustAPI |
|----------|-------|---------|---------|
| **Plain Text** | 9,492.88 | 1,780.61 | 15,836.77 |
| **JSON** | 6,537.78 | 2,210.73 | 14,531.13 |
| **Dynamic Path** | 5,991.23 | 2,118.87 | 176,624.28 |

## 🏆 Relative Performance (vs Flask)

### Plain Text
- **FastAPI**: 0.2x faster (1,780.61 RPS)
- **BustAPI**: 1.7x faster (15,836.77 RPS)

### JSON
- **FastAPI**: 0.3x faster (2,210.73 RPS)
- **BustAPI**: 2.2x faster (14,531.13 RPS)

### Dynamic Path
- **FastAPI**: 0.4x faster (2,118.87 RPS)
- **BustAPI**: 29.5x faster (176,624.28 RPS)

