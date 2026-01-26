# Sessions

BustAPI provides a secure, client-side session implementation. Sessions are stored in signed cookies, meaning the data is stored on the client but cannot be modified without the secret key.

## Configuration

To use sessions, you must set a `secret_key` on your application.

```python
from bustapi import BustAPI

app = BustAPI()
app.secret_key = "your-super-secret-key"  # Required for sessions
```

## Usage

Access the session object via the `session` proxy. It behaves like a standard Python directory.

### Storing Data

```python
from bustapi import session

@app.route("/login", methods=["POST"])
def login():
    # Store data
    session["username"] = "alice"
    session["user_id"] = 42
    return "Logged in"
```

### Retrieving Data

```python
@app.route("/profile")
def profile():
    user = session.get("username", "Guest")
    return f"Hello, {user}!"
```

### Removing Data

You can use `pop` or `del` to remove items.

```python
@app.route("/logout")
def logout():
    # Remove specific key
    session.pop("username", None)
    
    # Or clear entire session
    # session.clear()
    
    return "Logged out"
```

## Security

- **Signed Cookies**: Data is visible to the user (base64 encoded) but tamper-proof. **Do not store sensitive secrets** like passwords directly in the session.
- **Modifications**: BustAPI automatically tracks changes to the session dictionary (including `pop`, `clear`, etc.) and sends a new `Set-Cookie` header only when necessary.

## API Reference

The `session` object supports all standard dictionary methods:

- `session[key] = value`
- `session.get(key, default)`
- `session.pop(key, default)`
- `session.clear()`
- `session.update(dict)`
- `key in session`
