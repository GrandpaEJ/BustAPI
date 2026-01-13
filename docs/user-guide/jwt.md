# JWT Authentication

BustAPI provides Rust-backed JWT (JSON Web Token) authentication for high-performance token-based auth.

## Quick Start

```python
from bustapi import BustAPI, JWT, jwt_required

app = BustAPI(__name__)
app.secret_key = "your-secret-key"

jwt = JWT(app)

@app.post("/login")
def login():
    token = jwt.create_access_token(identity="user123")
    return {"access_token": token}

@app.get("/protected")
@jwt_required
def protected(request):
    return {"user": request.jwt_identity}
```

## JWT Class

### Initialization

```python
jwt = JWT(
    app,
    secret_key="optional-override",  # Uses app.secret_key if not set
    algorithm="HS256",               # HS256, HS384, HS512
    access_expires=900,              # 15 minutes (seconds)
    refresh_expires=2592000,         # 30 days (seconds)
)
```

### Creating Tokens

```python
# Access token (for API access)
token = jwt.create_access_token(
    identity="user123",
    expires_delta=3600,      # Custom expiry (optional)
    fresh=True,              # Fresh token from login
    claims={"role": "admin"} # Custom claims (optional)
)

# Refresh token (for getting new access tokens)
refresh = jwt.create_refresh_token(identity="user123")
```

### Decoding Tokens

```python
# Decode and verify
claims = jwt.decode_token(token)
# Returns: {"identity": "user123", "exp": ..., "iat": ..., "type": "access"}

# Verify only (returns bool)
is_valid = jwt.verify_token(token)

# Get identity (works on expired tokens)
identity = jwt.get_identity(token)
```

## Decorators

### @jwt_required

Require valid JWT in `Authorization: Bearer <token>` header.

```python
@app.get("/protected")
@jwt_required
def protected(request):
    user_id = request.jwt_identity  # User identity from token
    claims = request.jwt_claims     # All token claims
    return {"user": user_id}
```

### @jwt_optional

Allow both authenticated and anonymous access.

```python
@app.get("/feed")
@jwt_optional
def feed(request):
    if request.jwt_identity:
        return {"feed": "personalized for " + request.jwt_identity}
    return {"feed": "public"}
```

### @fresh_jwt_required

Require fresh token (from login, not from refresh).

```python
@app.post("/change-password")
@fresh_jwt_required
def change_password(request):
    # Only allow with fresh token
    return {"status": "password changed"}
```

### @jwt_refresh_token_required

Require refresh token for the token refresh endpoint.

```python
@app.post("/refresh")
@jwt_refresh_token_required
def refresh(request):
    new_token = jwt.create_access_token(
        identity=request.jwt_identity,
        fresh=False  # Refreshed tokens are not fresh
    )
    return {"access_token": new_token}
```

## Complete Example

```python
from bustapi import BustAPI, JWT, jwt_required, jwt_refresh_token_required
from bustapi.auth import hash_password, verify_password

app = BustAPI(__name__)
app.secret_key = "super-secret-key"
jwt = JWT(app)

# User database
USERS = {"admin": hash_password("secret")}

@app.post("/login")
def login(request):
    data = request.json
    if verify_password(data["password"], USERS.get(data["username"], "")):
        return {
            "access_token": jwt.create_access_token(data["username"]),
            "refresh_token": jwt.create_refresh_token(data["username"]),
        }
    return {"error": "Invalid credentials"}, 401

@app.post("/refresh")
@jwt_refresh_token_required
def refresh(request):
    return {"access_token": jwt.create_access_token(request.jwt_identity, fresh=False)}

@app.get("/me")
@jwt_required
def me(request):
    return {"user": request.jwt_identity}

if __name__ == "__main__":
    app.run()
```

## Algorithms

| Algorithm | Description |
|-----------|-------------|
| HS256 | HMAC-SHA256 (default, recommended) |
| HS384 | HMAC-SHA384 |
| HS512 | HMAC-SHA512 |

## Error Responses

- `401 Missing Authorization header` - No token provided
- `401 Token has expired` - Token past expiration
- `401 Invalid token signature` - Wrong secret key
- `401 Fresh token required` - Need fresh token for sensitive ops
