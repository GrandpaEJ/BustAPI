from typing import Optional

from bustapi import BustAPI, jsonify, request
from sqlmodel import Field, Session, SQLModel, create_engine, select

app = BustAPI()


# 1. Define Model
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


# 2. Create Engine (with check_same_thread=False for SQLite in multithreaded env)
# Note: BustAPI runs on multiple threads, so this flag is REQUIRED for SQLite.
sqlite_file_name = "example_sqlmodel.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


@app.before_request
def create_session():
    # Create a new session for each request
    request.session = Session(engine)


@app.teardown_request
def close_session(exception):
    # Close the session after request
    if hasattr(request, "session"):
        request.session.close()


@app.route("/init-db")
def init_db():
    SQLModel.metadata.create_all(engine)
    # Add seed data if empty
    with Session(engine) as session:
        if not session.exec(select(Item)).first():
            session.add(Item(name="Rust"))
            session.add(Item(name="Python"))
            session.commit()
    return jsonify({"status": "ok", "db": "initialized"})


@app.route("/items")
def list_items():
    # Use the session attached to request
    items = request.session.exec(select(Item)).all()
    # Convert to dicts for JSON serialization
    return jsonify([item.model_dump() for item in items])


@app.route("/items/<int:item_id>")
def get_item(item_id):
    item = request.session.get(Item, item_id)
    if not item:
        return jsonify({"error": "Not found"}), 404
    return jsonify(item.model_dump())


if __name__ == "__main__":
    print("Running SQLModel example on http://127.0.0.1:5010", flush=True)
    print("First run: curl http://127.0.0.1:5010/init-db", flush=True)
    # debug=False is required for tests to handle signals correctly
    app.run(port=5010, debug=False)
