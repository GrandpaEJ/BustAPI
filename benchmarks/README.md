# 🚀 Web Framework Benchmark Results

**Date:** 2025-12-09 20:11:26
**Config:** 15s duration, 4 threads, 100 connections

## 📊 Summary (Requests/sec)

| Endpoint | Flask | FastAPI | BustAPI |
|----------|-------|---------|---------|
| **Plain Text** | 10,720.70 | N/A | 18,704.24 |
| **JSON** | 8,932.19 | N/A | 17,254.74 |
| **Dynamic Path** | 8,088.44 | N/A | 165,276.50 |

## 🏆 Relative Performance (vs Flask)

### Plain Text
- **BustAPI**: 1.7x faster (18,704.24 RPS)

### JSON
- **BustAPI**: 1.9x faster (17,254.74 RPS)

### Dynamic Path
- **BustAPI**: 20.4x faster (165,276.50 RPS)

