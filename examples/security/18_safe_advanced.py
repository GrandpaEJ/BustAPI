import asyncio
import time

from bustapi import BustAPI
from bustapi.safe import Const, Integer, String, Struct, py

app = BustAPI()

# --- 1. Complex Data Models (Nested Structs) ---


class Address(Struct):
    city: String
    zipcode: Integer


class UserProfile(Struct):
    bio: String
    address: Address  # Nested Struct!


class User(Struct):
    username: String
    age: Integer
    role: Const("user")
    profile: UserProfile  # Nested Struct!


# --- 2. Real-world Background Tasks ---


async def send_welcome_email(username):
    print(f"📧 Sending welcome email to {username}...")
    await asyncio.sleep(1)  # Simulate network delay
    print(f"✅ Email sent to {username}")


async def analytics_event(event_type, data):
    print(f"📊 Logging analytics: {event_type} - {data}")
    await asyncio.sleep(0.5)


async def heavy_db_write(user_dict):
    print("💾 Saving user to DB...")
    await asyncio.sleep(2)
    print("✅ User saved!")


# --- 3. API Endpoints ---


@app.route("/register", methods=["POST"])
async def register():
    # Simulate incoming JSON body (BustAPI normally gives this via request.json)
    # Here we mock it for the example to be runnable standalone/via simple curl
    request_data = {
        "username": "grandpa_dev",
        "age": 80,
        "role": "user",
        "profile": {
            "bio": "Coding efficiently",
            "address": {"city": "Rustville", "zipcode": 12345},
        },
    }

    try:
        # 1. Validation: Recursive parsing from dict
        user = User(**request_data)
        print(f"✨ Validated User: {user.username} from {user.profile.address.city}")

        # 2. Concurrency: Launch multiple fire-and-forget tasks
        # These run in parallel in the background without blocking the response!
        py(send_welcome_email(user.username))
        py(analytics_event("registration", {"user": user.username}))
        py(heavy_db_write(request_data))

        return {
            "status": "success",
            "message": "User registered",
            "user": user.username,
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    app.run(port=5000)
