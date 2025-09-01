```markdown
Benchmarks

This folder contains a minimal benchmark harness to compare BustAPI, Flask and FastAPI.

Requirements
- Python 3.8+
- Install dev dependencies into a virtualenv:

   pip install httpx uvicorn fastapi flask

Quickstart

1. Start a single target:

    python benchmarks/run_bench.py --target bustapi --concurrency 50 --duration 10

2. Run all targets sequentially:

    python benchmarks/run_bench.py --target all --concurrency 50 --duration 10

Notes
- The script starts each app as a subprocess using the current Python interpreter.
- The FastAPI app runs via uvicorn inside the script `benchmarks/apps/fastapi_app.py`.
- For realistic benchmarks, prefer dedicated tools like wrk or vegeta and run the server in production mode.

```

## 🚀 Latest Performance Results

### Comprehensive Benchmark (New - 2025)
**BustAPI v0.1.5 Performance:**
- **Requests/sec**: 621.10 RPS
- **Total requests**: 9,350 (in 15 seconds)
- **Average response time**: 17.22ms
- **Error rate**: 0.00%
- **Test conditions**: 100 concurrent requests

### Historical Results (10,000 requests, measured in this workspace)

| Target   | Concurrency | Success | Errors | Elapsed (s) | RPS    |
|----------|-------------:|--------:|-------:|------------:|-------:|
| BustAPI  | 50          | 10049   | 0      | 16.06       | 625.54 |
| Flask    | 50          | 10049   | 0      | 15.82       | 635.29 |
| FastAPI  | 50          | 10049   | 0      | 14.87       | 675.60 |
| BustAPI  | 100         | 10099   | 0      | 16.77       | 602.36 |
| Flask    | 100         | 10099   | 0      | 15.66       | 644.77 |
| FastAPI  | 100         | 10099   | 0      | 15.08       | 669.68 |

## 📊 New Benchmark Tools

### `comprehensive_benchmark.py`
Complete performance testing suite with functionality validation, load testing, and memory monitoring.

### `framework_comparison.py`
Interactive framework comparison tool with automated server switching.

### `benchmark_server.py`
Optimized BustAPI server with multiple endpoints for comprehensive testing.

Notes about these runs
- Environment: ran inside this repository on Linux using a local virtualenv at `./.venv` created with `python3 -m venv .venv`.
- Packages installed into the venv for the benchmarks: `httpx`, `uvicorn`, `fastapi`, `flask`.
- Commands used (examples):
   - `./.venv/bin/python benchmarks/run_bench.py --target bustapi --concurrency 50 --requests 10000`
   - `./.venv/bin/python benchmarks/run_bench.py --target fastapi --concurrency 100 --requests 10000`
- The runner starts the target app as a subprocess and reports a small summary in `benchmarks/last_results.txt` after each run.

Interpretation
- These numbers are a quick, single-shot comparison for a tiny "hello world" endpoint on the same machine; they should not be used as a definitive benchmark. For reproducible, production-like results, run multiple trials on dedicated hardware and consider tools like wrk, vegeta, or k6.
