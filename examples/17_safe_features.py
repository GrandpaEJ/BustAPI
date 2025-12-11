import asyncio

from bustapi import BustAPI
from bustapi.safe import Const, Integer, String, Struct, py

app = BustAPI()


# --- 1. Type Safe Struct ---
class User(Struct):
    name: String
    age: Integer
    role: Const("admin")


# --- 2. Concurrency Helper ---
async def heavy_task(name, duration):
    print(f"⏳ Task '{name}' started (sleeping {duration}s)...")
    await asyncio.sleep(duration)
    print(f"✅ Task '{name}' finished!")


@app.route("/")
async def index():
    try:
        # Valid User
        u = User(name="Grandpa", age=80, role="admin")
        print(f"Created user: {u}")

        # Async Task
        py(heavy_task("Background Job", 2))

        return f"Hello {u.name}, background task started!"
    except Exception as e:
        return f"Error: {e}"


@app.route("/error")
def error_test():
    try:
        # Invalid User (WRONG role)
        u = User(name="Hacker", age=20, role="user")
        return "Should not reach here"
    except ValueError as e:
        return f"Caught expected validation error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


if __name__ == "__main__":
    app.run(port=5000)
