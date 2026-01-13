"""
Example: Middleware and Sessions in BustAPI

This example demonstrates how to use the new middleware system and built-in session management.
"""

from bustapi import BustAPI, Middleware, Response, redirect, session, url_for

app = BustAPI()

# 1. Setup Session Secret
# REQUIRED for signed cookies.
app.secret_key = "my-secure-secret-key"


# 2. Define Custom Middleware
class HeaderMiddleware(Middleware):
    """Adds a custom header to every response."""

    def process_response(self, request, response):
        response.headers["X-Powered-By"] = "BustAPI Middleware"
        return response


class AuthMiddleware(Middleware):
    """
    Simulates authentication check on /admin routes.
    Note: In real app, check session or headers.
    """

    def process_request(self, request):
        if request.path.startswith("/admin"):
            # Use request.session proxy directly if needed, or global session
            if not session.get("logged_in"):
                return Response("Forbidden: Login Required", status=403)
        return None


# 3. Register Middleware
app.middleware_manager.add(HeaderMiddleware())
app.middleware_manager.add(AuthMiddleware())


# 4. Define Routes
@app.route("/")
def index():
    user = session.get("username", "Guest")
    login_status = "Logged In" if session.get("logged_in") else "Logged Out"

    html = f"""
    <h1>Welcome, {user}</h1>
    <p>Status: {login_status}</p>
    <p>Visit <a href="/admin">/admin</a> (Required Login)</p>
    <hr>
    <h3>Actions</h3>
    <ul>
        <li><a href="/login/alice">Login as Alice</a></li>
        <li><a href="/login/bob">Login as Bob</a></li>
        <li><a href="/logout">Logout</a></li>
    </ul>
    """
    return Response(html, headers={"Content-Type": "text/html"})


@app.route("/login/<name>")
def login(name):
    # Set session data
    session["username"] = name
    session["logged_in"] = True
    session.permanent = True  # Optional: Make session persistent
    return redirect("/")


@app.route("/logout")
def logout():
    # Clear session
    session.clear()
    return redirect("/")


@app.route("/admin")
def admin():
    # This route is protected by AuthMiddleware
    return "<h1>Admin Panel</h1><p>You have access!</p>"


if __name__ == "__main__":
    print("Running Middleware & Session Example")
    print("Try accessing http://127.0.0.1:8080")
    app.run(debug=True, port=8080)
