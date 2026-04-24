# Security

BustAPI 0.3.0 introduces a dedicated Security extension to handle common protection mechanisms.

## Initialization

```python
from bustapi import BustAPI, Security

app = BustAPI()
security = Security(app)
```

## Rate Limiting

Rate limiting is backed by a Rust implementation using the Token Bucket algorithm, making it extremely fast.

```python
from bustapi import RateLimit

limiter = RateLimit(app)

@app.route("/api/fast")
@limiter.limit("100/minute")
def fast_api():
    return "This route is limited to 100 requests per minute"
```

You can define limits per second, minute, hour, or day.

## CORS (Cross-Origin Resource Sharing)

Enable CORS to allow browsers to make requests from other domains.

```python
# Enable CORS for all origins
security.enable_cors()

# Or restrict it
security.enable_cors(origins=["https://myapp.com"], methods=["GET", "POST"])
```

## Security Headers

Automatically add headers to protect against XSS, clickjacking, and more.

```python
# Enables: X-Frame-Options, X-XSS-Protection, X-Content-Type-Options
security.enable_secure_headers()

# Also enables Strict-Transport-Security (HSTS)
security.enable_secure_headers(hsts=True)
```
