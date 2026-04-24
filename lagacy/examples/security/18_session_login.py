"""
Example: Session-based Login with BustAPI

Flask-Login style authentication using sessions.

Run:
    python examples/18_session_login.py

Test with:
    # Visit login page
    curl http://localhost:5000/login

    # Login (form submit)
    curl -X POST http://localhost:5000/login -d "username=admin&password=secret"

    # Access dashboard (use cookie from login)
    curl http://localhost:5000/dashboard --cookie "session=..."
"""

from bustapi import BustAPI, redirect, request, session
from bustapi.auth import (
    BaseUser,
    LoginManager,
    current_user,
    hash_password,
    login_required,
    login_user,
    logout_user,
    roles_required,
    verify_password,
)

app = BustAPI(__name__)
app.secret_key = "your-secret-key-change-in-production"

# Initialize LoginManager
login_manager = LoginManager(app)


# Simulated User class
class User(BaseUser):
    def __init__(self, id, username, password_hash, role="user"):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role

    @property
    def roles(self):
        return [self.role]


# Simulated database
USERS = {
    "1": User("1", "admin", hash_password("secret"), role="admin"),
    "2": User("2", "user", hash_password("password"), role="user"),
}

USERNAME_TO_ID = {"admin": "1", "user": "2"}


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID from database."""
    return USERS.get(user_id)


@app.get("/")
def home():
    """Public home page."""
    if current_user.is_authenticated:
        return f"Hello, {current_user.username}! <a href='/dashboard'>Dashboard</a> | <a href='/logout'>Logout</a>"
    return "Welcome! <a href='/login'>Login</a>"


@app.get("/login")
def login_page():
    """Login form."""
    return """
    <h1>Login</h1>
    <form method="POST">
        <input name="username" placeholder="Username"><br>
        <input name="password" type="password" placeholder="Password"><br>
        <button type="submit">Login</button>
    </form>
    <p>Try: admin/secret or user/password</p>
    """


@app.post("/login")
def login():
    """Handle login form submission."""
    username = request.form.get("username")
    password = request.form.get("password")

    user_id = USERNAME_TO_ID.get(username)
    if not user_id:
        return "Invalid username", 401

    user = USERS.get(user_id)
    if not user or not verify_password(password, user.password_hash):
        return "Invalid password", 401

    # Log in the user
    login_user(user, remember=True)

    return redirect("/dashboard")


@app.get("/logout")
def logout():
    """Log out current user."""
    logout_user()
    return redirect("/")


@app.get("/dashboard")
@login_required
def dashboard():
    """Protected dashboard - requires login."""
    return f"""
    <h1>Dashboard</h1>
    <p>Welcome, {current_user.username}!</p>
    <p>Role: {current_user.role}</p>
    <a href="/admin">Admin Panel</a> | <a href="/logout">Logout</a>
    """


@app.get("/admin")
@roles_required("admin")
def admin_panel():
    """Admin-only page."""
    return f"""
    <h1>Admin Panel</h1>
    <p>Hello, {current_user.username}! You have admin access.</p>
    <a href="/dashboard">Back to Dashboard</a>
    """


if __name__ == "__main__":
    print("Session Login Example")
    print("-" * 40)
    print("Users:")
    print("  admin / secret (role: admin)")
    print("  user / password (role: user)")
    print("-" * 40)
    app.run(debug=True)
