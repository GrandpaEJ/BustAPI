# Database Integration

You can integrate any database library (SQLAlchemy, SQLite, etc.) using request hooks.

## Request Hooks

- `before_request`: Runs before the route handler.
- `after_request`: Runs after the route handler.
- `teardown_request`: Runs after the request is finished (even if an error occurred).

## SQLite Example

```python
import sqlite3
from bustapi import BustAPI, g

app = BustAPI()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('test.db')
    return g.db

@app.teardown_request
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route("/users")
def list_users(request):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users")
    return {"users": cur.fetchall()}
```
