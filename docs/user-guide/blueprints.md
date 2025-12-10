# Blueprints

As your application grows, you usually want to organize your code into multiple files or modules. **Blueprints** provide a way to group related routes and resources.

## Creating a Blueprint

```python title="routes/auth.py"
from bustapi import Blueprint

auth_bp = Blueprint("auth", url_prefix="/auth")

@auth_bp.route("/login")
def login():
    return "Login Page"

@auth_bp.route("/register")
def register():
    return "Register Page"
```

## Registering a Blueprint

You register the blueprint on your main application instance.

```python title="app.py"
from bustapi import BustAPI
from routes.auth import auth_bp

app = BustAPI()
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run()
```

Now your routes will be accessible at:

- `/auth/login`
- `/auth/register`

## Blueprint Templates and Static Files

Blueprints can define their own static and template folders.

```python
admin = Blueprint("admin", url_prefix="/admin",
                  template_folder="admin/templates",
                  static_folder="admin/static")
```

This allows you to create reusable modular applications.
