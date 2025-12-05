# 🚀 Web Framework Benchmark Results

This benchmark compares the performance of BustAPI (a high-performance Flask-compatible web framework) against Flask and FastAPI using the `wrk` HTTP benchmarking tool.

## Benchmark Configuration
- **Tool:** wrk (https://github.com/wg/wrk)
- **Duration:** 15 seconds per endpoint
- **Threads:** 4
- **Connections:** 100
- **Date:** 2025-12-05 21:45:18
- **System:** Linux 6.14, Python 3.13.10

## Server Configurations
- **Flask:** Gunicorn with 4 sync workers
- **FastAPI:** Uvicorn with 4 workers
- **BustAPI:** Built-in multi-threaded server

## Framework Versions
- **Flask:** 3.1.2
- **Gunicorn:** 23.0.0
- **FastAPI:** 0.123.9
- **Uvicorn:** 0.38.0
- **BustAPI:** 0.2.0

## Test Endpoints
- **Plain Text:** Simple string response
- **JSON:** JSON object response
- **Dynamic Path:** URL parameter parsing and response

## 📊 Summary (Requests/sec)

| Endpoint | Flask | FastAPI | BustAPI |
|----------|-------|---------|---------|
| **Plain Text** | 3,244.81 | 1,892.08 | 19,929.01 |
| **JSON** | 3,241.30 | 1,900.03 | 17,595.42 |
| **Dynamic Path** | 3,251.00 | 2,028.98 | 175,923.13 |

## 🏆 Relative Performance (vs Flask)

### Plain Text
- **FastAPI**: 0.6x faster (1,892.08 RPS)
- **BustAPI**: 6.1x faster (19,929.01 RPS)

### JSON
- **FastAPI**: 0.6x faster (1,900.03 RPS)
- **BustAPI**: 5.4x faster (17,595.42 RPS)

### Dynamic Path
- **FastAPI**: 0.6x faster (2,028.98 RPS)
- **BustAPI**: 54.1x faster (175,923.13 RPS)

