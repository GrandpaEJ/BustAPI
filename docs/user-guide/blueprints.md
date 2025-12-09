# Blueprints

Blueprints allow you to organize your application into modular components.

## Creating a Blueprint

```python
# auth.py
from bustapi import Blueprint

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login")
def login(request):
    return "Login Page"
```

## Registering a Blueprint

```python
# app.py
from bustapi import BustAPI
from auth import auth_bp

app = BustAPI()
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run()
```

This will make the login route accessible at `/auth/login`.
