# Dependency Injection

Dependency Injection (DI) is a design pattern that allows you to decouple components. BustAPI borrows the `Depends` system from FastAPI to make this extremely easy.

## Why use DI?

- **Reusability**: Write logic once (like extracting a token), use it everywhere.
- **Testing**: Easily override dependencies during tests.
- **Clean Code**: Minimize boilerplate in your view functions.

## Basic Usage

```python
from bustapi import Depends

# A reusable dependency
def get_query_params(q: str = None, limit: int = 100):
    return {"q": q, "limit": limit}

@app.route("/items")
def items(params: dict = Depends(get_query_params)):
    # BustAPI calls get_query_params() and injects the result
    return params
```

## Dependency Graph

Dependencies can depend on other dependencies. BustAPI resolves the graph and caches the results per request.

```python
def get_token(x_token: str = Header(...)):
    if x_token != "secret":
        abort(400)
    return x_token

def get_user_from_token(token: str = Depends(get_token)):
    # This won't run if get_token fails/aborts
    return User.find(token=token)

@app.route("/me")
def me(user = Depends(get_user_from_token)):
    return user
```
