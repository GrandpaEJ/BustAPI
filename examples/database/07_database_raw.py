import sqlite3

from bustapi import BustAPI, jsonify, request

app = BustAPI()
DB_FILE = "example.db"


def get_db_connection():
    # check_same_thread=False is required because BustAPI runs on a multi-threaded Rust server.
    # timeout=10 helps prevent 'database locked' errors during tests.
    conn = sqlite3.connect(DB_FILE, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@app.before_request
def connect_db():
    request.db = get_db_connection()


@app.teardown_request
def close_db(exception):
    """Close DB connection."""
    if hasattr(request, "db"):
        request.db.close()


@app.route("/init-db")
def init_db():
    conn = get_db_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO items (name) VALUES ('Rust')")
    conn.execute("INSERT INTO items (name) VALUES ('Python')")
    conn.commit()
    conn.close()
    return jsonify({"message": "Database initialized"})


@app.route("/items")
def list_items():
    cursor = request.db.execute("SELECT * FROM items")
    items = [{"id": row["id"], "name": row["name"]} for row in cursor.fetchall()]
    return jsonify(items)


if __name__ == "__main__":
    print("Running database example on http://127.0.0.1:5006")
    print("First run: curl http://127.0.0.1:5006/init-db")
    app.run(port=5006, debug=False)
