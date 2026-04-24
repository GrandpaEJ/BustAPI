# Validation

Validating incoming data is critical for security and stability. BustAPI includes a robust validation system based on strict types.

## The `Struct` Class

Define your data schemas by subclassing `Struct` and using the special types provided by `bustapi.safe`.

!!! note "Supported Types"
    - `String`
    - `Integer`
    - `Float`
    - `Boolean`
    - `Array(Type)`: List of items

## Example Schema

```python
from bustapi.safe import Struct, String, Integer, Array

class Address(Struct):
    street: String
    city: String
    zip: Integer

class User(Struct):
    name: String
    age: Integer
    tags: Array(String)
    address: Address  # Nested Struct!
```

## Using in Routes

Simply type-hint your route parameter. BustAPI handles parsing, validation, and error reporting (422 Unprocessable Entity) automatically.

```python
from bustapi import Body

@app.post("/users")
def create_user(user: User = Body(...)):
    # If we get here, 'user' is guaranteed to be valid
    # user.address.city is accessible directly
    return {"message": "User valid"}
```
