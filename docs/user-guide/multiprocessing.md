# Multiprocessing

BustAPI v0.8.0 introduces native multiprocessing for maximum throughput.

## Quick Start

```python
from bustapi import BustAPI

app = BustAPI()

@app.route("/")
def hello():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, workers=4)
```

With `workers=4`, BustAPI spawns 4 worker processes that share the same port.

---

## Platform Behavior

| Platform | Mode | Performance | How It Works |
|:---------|:-----|------------:|:-------------|
| 🐧 **Linux** | Multiprocessing | **100,000+ RPS** | `SO_REUSEPORT` kernel load balancing |
| 🍎 macOS | Single-process | ~35,000 RPS | Actix-web internal threading |
| 🪟 Windows | Single-process | ~17,000 RPS | Actix-web internal threading |

---

## Linux: SO_REUSEPORT

On Linux, BustAPI uses `SO_REUSEPORT` for true multiprocessing:

```
┌──────────────────────────────────────┐
│           Linux Kernel               │
│      SO_REUSEPORT Load Balancer      │
└─────────────┬────────────────────────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐
│Worker1│ │Worker2│ │Worker3│
│ PID:1 │ │ PID:2 │ │ PID:3 │
└───────┘ └───────┘ └───────┘
```

Each worker is a separate process, eliminating Python's GIL bottleneck.

### How It Works

1. **Parent process** calls `app.run(workers=4)`
2. BustAPI `fork()`s 4 child processes
3. Each child binds to the same port with `SO_REUSEPORT`
4. Linux kernel distributes incoming connections across workers
5. Signal handlers gracefully shut down all workers on `Ctrl+C`

---

## Worker Count Recommendations

| Use Case | Workers | Notes |
|:---------|--------:|:------|
| Development | 1 | `debug=True` ignores `workers` |
| Production (4 cores) | 4 | Match CPU cores |
| Production (8 cores) | 8 | Scale with cores |
| High I/O workloads | 2x cores | If I/O-bound |

```python
import os

# Auto-detect CPU count
workers = os.cpu_count() or 4

app.run(workers=workers)
```

---

## Performance Benchmarks

Tested on Python 3.13, Intel i5-8365U (8 cores), Ubuntu Linux:

| Workers | RPS (Root) | RPS (JSON) |
|--------:|-----------:|-----------:|
| 1 | ~25,000 | ~20,000 |
| 2 | ~50,000 | ~45,000 |
| 4 | ~100,000 | ~90,000 |
| 8 | ~105,000 | ~99,000 |

Performance scales linearly up to CPU core count.

---

## Graceful Shutdown

BustAPI handles `SIGINT` (Ctrl+C) and `SIGTERM` gracefully:

```
🚀 Starting 4 worker processes (Linux SO_REUSEPORT)...
┌──────────────────────────────────────────────────────┐
│                    BustAPI v0.8.0                    │
│                http://0.0.0.0:5000                   │
│  Handlers ............. 5   Processes ........... 1  │
└──────────────────────────────────────────────────────┘
^C
🛑 Shutting down workers...
```

All workers receive termination signals and exit cleanly.

---

## macOS / Windows Fallback

On macOS and Windows, `workers` parameter is still respected but uses Actix-web's internal thread pool:

```
[BustAPI] Starting server on macOS (single process mode)...
[BustAPI] Note: Multi-worker mode requires SO_REUSEPORT (Linux only)
```

The server still runs efficiently using async I/O and threading, but without separate process isolation.

---

## Best Practices

1. **Always deploy on Linux** for production
2. **Set workers = CPU cores** for optimal performance
3. **Use `debug=False`** in production
4. **Monitor memory** - each worker uses ~25-40MB

```python
if __name__ == "__main__":
    import os
    
    app.run(
        host="0.0.0.0",
        port=5000,
        workers=os.cpu_count() or 4,
        debug=False
    )
```
