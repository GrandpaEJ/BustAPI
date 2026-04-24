# Session Authentication

Flask-Login style session-based authentication for BustAPI.

## Quick Start

```python
from bustapi import BustAPI
from bustapi.auth import LoginManager, login_user, logout_user, current_user, login_required

app = BustAPI(__name__)
app.secret_key = "your-secret-key"

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.get("/dashboard")
@login_required
def dashboard():
    return f"Hello, {current_user.username}!"
```

## LoginManager

### Setup

```python
from bustapi.auth import LoginManager

login_manager = LoginManager(app)

# Configure
login_manager.login_view = "auth.login"  # Redirect for @login_required
login_manager.login_message = "Please log in first"
```

### User Loader

Register a function to load users by ID:

```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
```

## User Classes

### BaseUser

Mixin for user models with sensible defaults:

```python
from bustapi.auth import BaseUser

class User(db.Model, BaseUser):
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password_hash = Column(String)
    
    # BaseUser provides:
    # - is_authenticated = True
    # - is_active = True
    # - is_anonymous = False
    # - get_id() returns str(self.id)
```

### AnonUser

Placeholder for unauthenticated users:

```python
from bustapi.auth import AnonUser

anon = AnonUser()
anon.is_authenticated  # False
anon.is_anonymous      # True
```

## Login / Logout

```python
from bustapi.auth import login_user, logout_user

@app.post("/login")
def login(request):
    user = User.authenticate(request.form["email"], request.form["password"])
    if user:
        login_user(user, remember=True)  # remember=True for persistent session
        return redirect("/dashboard")
    return "Invalid credentials", 401

@app.get("/logout")
def logout():
    logout_user()
    return redirect("/")
```

## current_user

Access the logged-in user anywhere:

```python
from bustapi.auth import current_user

@app.get("/profile")
def profile():
    if current_user.is_authenticated:
        return f"Welcome, {current_user.username}"
    return "Please log in"
```

## Decorators

### @login_required

Require authenticated user:

```python
from bustapi.auth import login_required

@app.get("/dashboard")
@login_required
def dashboard():
    return f"Hello, {current_user.username}!"
```

### @fresh_login_required

Require fresh session (from login, not remember-me):

```python
from bustapi.auth import fresh_login_required

@app.post("/change-password")
@fresh_login_required
def change_password():
    # Sensitive operation - require recent login
    ...
```

### @roles_required

Require specific role(s):

```python
from bustapi.auth import roles_required

@app.get("/admin")
@roles_required("admin")
def admin_panel():
    return "Admin only"

@app.get("/moderator")
@roles_required("admin", "moderator")
def mod_panel():
    return "Admin or moderator"
```

### @permission_required

Require specific permission(s):

```python
from bustapi.auth import permission_required

@app.post("/delete")
@permission_required("delete_posts")
def delete_post():
    ...
```

## Password Hashing

Argon2id password hashing (OWASP recommended):

```python
from bustapi.auth import hash_password, verify_password

# Hash a password
hashed = hash_password("user_password")
# Returns: "$argon2id$v=19$m=65536,t=3,p=4$..."

# Verify password
if verify_password("user_password", hashed):
    print("Password correct!")
```

## Token Generation

Secure random tokens for CSRF, password reset, etc:

```python
from bustapi.auth import generate_token, generate_csrf_token

# Generate token (default 32 bytes = 64 hex chars)
token = generate_token()

# Generate CSRF token
csrf = generate_csrf_token()
```

## CSRF Protection

```python
from bustapi.auth import CSRFProtect

csrf = CSRFProtect(app)

# In templates:
# <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

# Exempt a route
@csrf.exempt
@app.post("/api/webhook")
def webhook():
    ...
```

## Complete Example

```python
from bustapi import BustAPI, redirect
from bustapi.auth import (
    LoginManager, BaseUser, login_user, logout_user, current_user,
    login_required, roles_required, hash_password, verify_password
)

app = BustAPI(__name__)
app.secret_key = "your-secret"
login_manager = LoginManager(app)

class User(BaseUser):
    def __init__(self, id, username, password_hash, role="user"):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
    
    @property
    def roles(self):
        return [self.role]

USERS = {"1": User("1", "admin", hash_password("secret"), "admin")}

@login_manager.user_loader
def load_user(user_id):
    return USERS.get(user_id)

@app.post("/login")
def login(request):
    user = USERS.get("1")
    if verify_password(request.form["password"], user.password_hash):
        login_user(user)
        return redirect("/dashboard")
    return "Invalid", 401

@app.get("/dashboard")
@login_required
def dashboard():
    return f"Hello, {current_user.username}!"

@app.get("/admin")
@roles_required("admin")
def admin():
    return "Admin panel"

if __name__ == "__main__":
    app.run()
```
