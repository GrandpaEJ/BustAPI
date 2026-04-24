# Blueprints

As your application grows, putting everything in one file becomes unmanageable. Blueprints allow you to organize your code into reusable modules.

## The Concept

A Blueprint is like a mini-application. It can have its own routes, templates, and static files. However, it cannot run on its own; it must be registered with a `BustAPI` application.

## Defining a Blueprint

!!! note "File: routes/auth.py"
    ```python
    from bustapi import Blueprint

    # Create the blueprint
    auth_bp = Blueprint("auth", url_prefix="/auth")

    @auth_bp.route("/login")
    def login():
        return "Login Page"

    @auth_bp.route("/logout")
    def logout():
        return "Logout Page"
    ```

## Registering a Blueprint

!!! note "File: app.py"
    ```python
    from bustapi import BustAPI
    from routes.auth import auth_bp

    app = BustAPI()

    # Register the blueprint
    app.register_blueprint(auth_bp)

    # Logic is now served at /auth/login and /auth/logout
    ```

## Recommended Structure

For medium-sized projects, we recommend a package-based structure.

```
/myproject
    __init__.py
    app.py
    /blueprints
        __init__.py
        auth.py
        admin.py
        api.py
    /static
    /templates
```
