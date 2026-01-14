"""
Complex Dynamic REST API Benchmark
Tests realistic API patterns: path params, query params, POST bodies, business logic
"""

from bustapi import BustAPI, jsonify, request

app = BustAPI()

# In-memory "database"
USERS = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 28},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 34},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com", "age": 22},
}

POSTS = {
    1: {
        "id": 1,
        "user_id": 1,
        "title": "Hello World",
        "body": "First post!",
        "likes": 42,
    },
    2: {
        "id": 2,
        "user_id": 1,
        "title": "BustAPI Rocks",
        "body": "So fast!",
        "likes": 128,
    },
    3: {
        "id": 3,
        "user_id": 2,
        "title": "Python Tips",
        "body": "Use type hints",
        "likes": 55,
    },
}

# ============== TURBO ROUTES (Zero Overhead) ==============
# Static responses, no params needed


@app.turbo_route("/api/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}


@app.turbo_route("/api/stats")
def stats():
    return {
        "total_users": len(USERS),
        "total_posts": len(POSTS),
        "total_likes": sum(p["likes"] for p in POSTS.values()),
    }


# ============== REGULAR ROUTES (Full Features) ==============
# Dynamic responses with path/query params


@app.route("/api/users")
def list_users():
    return list(USERS.values())


@app.route("/api/users/<int:id>")
def get_user(id):
    user = USERS.get(id)
    if not user:
        return {"error": "User not found"}, 404
    return user


@app.route("/api/users/<int:id>/posts")
def get_user_posts(id):
    user_posts = [p for p in POSTS.values() if p["user_id"] == id]
    return user_posts


@app.route("/api/posts")
def list_posts():
    # Query param support: ?limit=X
    limit = request.args.get("limit", type=int, default=10)
    posts = list(POSTS.values())[:limit]
    return posts


@app.route("/api/posts/<int:id>")
def get_post(id):
    post = POSTS.get(id)
    if not post:
        return {"error": "Post not found"}, 404
    return post


@app.route("/api/posts/<int:id>/like", methods=["POST"])
def like_post(id):
    post = POSTS.get(id)
    if not post:
        return {"error": "Post not found"}, 404
    post["likes"] += 1
    return {"success": True, "new_likes": post["likes"]}


@app.route("/api/search")
def search():
    # Complex query: ?q=term&type=users|posts
    query = request.args.get("q", "")
    search_type = request.args.get("type", "all")

    results = {"users": [], "posts": []}

    if search_type in ("users", "all"):
        results["users"] = [
            u for u in USERS.values() if query.lower() in u["name"].lower()
        ]

    if search_type in ("posts", "all"):
        results["posts"] = [
            p for p in POSTS.values() if query.lower() in p["title"].lower()
        ]

    return results


@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()
    new_id = max(USERS.keys()) + 1
    user = {
        "id": new_id,
        "name": data.get("name", "Anonymous"),
        "email": data.get("email", ""),
        "age": data.get("age", 0),
    }
    USERS[new_id] = user
    return user, 201


if __name__ == "__main__":
    print("Complex Dynamic REST API")
    print("=" * 40)
    print("Turbo routes: /api/health, /api/stats")
    print("Dynamic routes: /api/users, /api/posts, /api/search")
    print("=" * 40)
    app.run(host="127.0.0.1", port=5000, workers=8, debug=False)
