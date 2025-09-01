from fastapi import FastAPI
import time
import uvicorn

app = FastAPI(title="FastAPI Benchmark Server", version="1.0.0")

users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
]


@app.get("/")
def root():
    return {
        "message": "FastAPI Benchmark Server",
        "version": "1.0.0",
        "timestamp": time.time(),
        "status": "running",
    }


@app.get("/api/test")
def api_test():
    return {
        "test": True,
        "framework": "FastAPI",
        "performance": "async",
        "timestamp": time.time(),
    }


@app.get("/api/users")
def get_users():
    return {"users": users, "count": len(users), "timestamp": time.time()}


if __name__ == "__main__":
    print("🚀 Starting FastAPI Benchmark Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
