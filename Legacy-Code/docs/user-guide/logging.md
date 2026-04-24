# Request Logging

Starting from **v0.9.0**, BustAPI uses a high-performance **Rust-native logging system**.

## Features

- **Zero-Overhead**: Logging happens in the Rust backend, avoiding Python GIL contention.
- **Full Coverage**: Captures ALL requests, including:
    - ✅ **Static Files** (`/static/video.mp4`)
    - ✅ **404 Not Found** errors
    - ✅ **Browser Probes** (HEAD requests)
    - ✅ **Fast Rust Routes**
- **Accurate Latency**: Timings are measured in Rust with microsecond precision.
- **Color Coded**: Easy to read output with status code coloring.

## Configuration

Logging is configured via the `app.run()` method:
 
```python
# Standard Debug Mode (Summary logs only)
app.run(debug=True)
 
# Verbose Mode (Detailed headers + Tracing)
app.run(debug=True, verbose=True)
```
 
### Modes
 
| Mode | Flag | Output Description |
| :--- | :--- | :--- |
| **Standard** | `debug=True` | **Summary only**. clean one-line logs: `TIME | STATUS | LATENCY | METHOD | PATH`. |
| **Verbose** | `verbose=True` | **Full Details**. Includes request headers, tracing events, and internal debug info. |
| **Production**| `debug=False`| **Minimal**. Only startup banner and Errors. |

### Custom Logging

You can use the `bustapi.logging` module to customize the logger or use it manually:

```python
from bustapi import BustAPI, logging

# Create a logger instance
logger = logging.BustAPILogger(use_colors=True)

# Log a custom request (useful for testing)
logger.log_request("GET", "/custom-path", 200, 0.005)
```

## Output Format

The log format is structured as:

`TIME | STATUS | LATENCY | METHOD | PATH`

Example:
```
14:32:01 | 200     | 45.120μs   | GET     | /
14:32:02 | 206     | 1.250ms    | GET     | /static/video.mp4
14:32:05 | 404     | 12.000μs   | GET     | /invalid
```

- **Status Colors**:
    - `2xx`: Green
    - `3xx`: Cyan
    - `4xx`: Yellow
    - `5xx`: Red
    - `HEAD`: Magenta
