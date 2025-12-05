from fastapi import FastAPI
import uvicorn

app = FastAPI()

from fastapi.responses import PlainTextResponse

# 1. Plain Text
@app.get("/", response_class=PlainTextResponse)
def index():
    return "Hello, World!"

# 2. JSON
@app.get("/json")
def json_endpoint():
    return {"message": "Hello, World!"}

# 3. Dynamic Path
@app.get("/user/{user_id}")
def user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}

if __name__ == "__main__":
    # Run with single worker to be comparable to other single-process tests
    # or use production settings. For fair comparison with BustAPI (multi-threaded),
    # we might want to let uvicorn use workers, but usually benchmarks compare single core performance
    # or max throughput. Let's stick to default for now, or maybe workers=1.
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")
