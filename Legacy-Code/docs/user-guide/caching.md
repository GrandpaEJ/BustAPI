# Response Caching

BustAPI v0.8.0 introduces built-in response caching for turbo routes.

## Quick Start

```python
from bustapi import BustAPI

app = BustAPI()

@app.turbo_route("/", cache_ttl=60)  # Cache for 60 seconds
def hello():
    return {"message": "Hello, World!"}
```

With `cache_ttl=60`, the response is cached for 60 seconds. Subsequent requests return instantly without calling your handler.

---

## Performance Impact

| Route Type | RPS | Latency |
|:-----------|----:|--------:|
| Regular `@app.route()` | ~25,000 | ~2ms |
| Turbo `@app.turbo_route()` | ~30,000 | ~1.5ms |
| **Cached Turbo** | **~140,000** | **<1ms** |

Caching provides a **5x performance boost** for frequently accessed endpoints.

---

## Use Cases

### Static Content

```python
@app.turbo_route("/about", cache_ttl=3600)  # 1 hour
def about():
    return {"company": "BustAPI Inc.", "version": "0.8.0"}
```

### Configuration Endpoints

```python
@app.turbo_route("/config", cache_ttl=300)  # 5 minutes
def config():
    return load_config_from_database()
```

### Health Checks

```python
@app.turbo_route("/health", cache_ttl=5)  # 5 seconds
def health():
    return {"status": "healthy", "db": check_db()}
```

---

## Cache Behavior

- **Per-route caching**: Each endpoint has its own cache
- **URL-based keys**: Different URLs = different cache entries
- **TTL-based expiration**: Cache automatically expires after `cache_ttl` seconds
- **In-memory storage**: Fast, no external dependencies

### Path Parameters

Path parameters create separate cache entries:

```python
@app.turbo_route("/users/<int:id>", cache_ttl=60)
def get_user(id: int):
    return {"id": id, "name": f"User {id}"}
```

- `/users/1` → cached separately from `/users/2`
- Each user ID has its own 60-second cache

---

## When NOT to Use Caching

❌ **Don't cache** when:

- Response depends on request body (POST data)
- Response is user-specific (authentication required)
- Data changes frequently
- Response is large (memory concern)

For these cases, use regular `@app.route()`:

```python
@app.route("/users/me")  # No caching - user-specific
def get_current_user():
    user = get_user_from_session()
    return {"id": user.id, "name": user.name}
```

---

## Cache Invalidation

Currently, cached responses expire automatically based on `cache_ttl`. Manual cache invalidation is planned for future releases.

**Workaround**: Use a short `cache_ttl` for data that changes frequently:

```python
@app.turbo_route("/stats", cache_ttl=10)  # Refresh every 10 seconds
def stats():
    return get_live_stats()
```

---

## Best Practices

1. **Start with short TTLs** (5-30 seconds) and increase based on needs
2. **Use caching for read-heavy endpoints** (homepage, about, config)
3. **Don't cache authenticated endpoints** unless using separate auth middleware
4. **Monitor memory usage** if caching large responses

```python
# Good: Frequently accessed, rarely changes
@app.turbo_route("/", cache_ttl=60)
def home():
    return {"message": "Welcome!"}

# Good: Expensive computation, OK to be slightly stale
@app.turbo_route("/leaderboard", cache_ttl=300)
def leaderboard():
    return compute_leaderboard()

# Bad: User-specific data
@app.turbo_route("/dashboard", cache_ttl=60)  # ❌ Don't do this
def dashboard():
    return get_user_dashboard()  # Different per user!
```
