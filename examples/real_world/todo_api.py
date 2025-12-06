#!/usr/bin/env python3
"""
Complete TODO API Example

This is a comprehensive real-world example demonstrating:
- RESTful API design
- Data validation with Pydantic
- Error handling
- Authentication (JWT)
- Database operations (SQLite)
- Auto documentation
- Testing endpoints
"""

import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional

import jwt
from bustapi import BustAPI, request
from pydantic import BaseModel, validator

from bustapi.docs import BustAPIDocs

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
DATABASE = "todos.db"

app = BustAPI()

# Initialize docs
docs = BustAPIDocs(
    app,
    title="TODO API",
    description="A complete TODO management API with authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Pydantic Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @validator("username")
    def username_must_be_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v

    @validator("password")
    def password_must_be_strong(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None

    @validator("priority")
    def priority_must_be_valid(cls, v):
        if v not in ["low", "medium", "high"]:
            raise ValueError("Priority must be low, medium, or high")
        return v


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    completed: bool
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    user_id: int


# Database setup
def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Todos table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'medium',
            completed BOOLEAN DEFAULT FALSE,
            due_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """
    )

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hashed


def create_jwt_token(user_id: int, username: str) -> str:
    """Create a JWT token for authentication"""
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    """Get current user from JWT token in Authorization header"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    payload = verify_jwt_token(token)
    return payload


# Authentication endpoints
@app.post("/auth/register", summary="Register new user", tags=["Authentication"])
def register(user: UserCreate):
    """Register a new user account"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        # Check if user already exists
        cursor.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (user.username, user.email),
        )
        if cursor.fetchone():
            return {"error": "Username or email already exists"}, 400

        # Create new user
        password_hash = hash_password(user.password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (user.username, user.email, password_hash),
        )
        user_id = cursor.lastrowid
        conn.commit()

        # Create JWT token
        token = create_jwt_token(user_id, user.username)

        return {
            "message": "User registered successfully",
            "user_id": user_id,
            "username": user.username,
            "token": token,
        }, 201

    except sqlite3.Error as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        conn.close()


@app.post("/auth/login", summary="Login user", tags=["Authentication"])
def login(credentials: UserLogin):
    """Login with username and password"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (credentials.username,),
        )
        user = cursor.fetchone()

        if not user or not verify_password(credentials.password, user[2]):
            return {"error": "Invalid username or password"}, 401

        token = create_jwt_token(user[0], user[1])

        return {
            "message": "Login successful",
            "user_id": user[0],
            "username": user[1],
            "token": token,
        }

    except sqlite3.Error as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        conn.close()


# TODO endpoints
@app.get(
    "/todos",
    response_model=List[TodoResponse],
    summary="Get user's todos",
    tags=["Todos"],
)
def get_todos(completed: Optional[bool] = None, priority: Optional[str] = None):
    """Get all todos for the authenticated user"""
    current_user = get_current_user()
    if not current_user:
        return {"error": "Authentication required"}, 401

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        query = "SELECT * FROM todos WHERE user_id = ?"
        params = [current_user["user_id"]]

        if completed is not None:
            query += " AND completed = ?"
            params.append(completed)

        if priority:
            query += " AND priority = ?"
            params.append(priority)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        todos = cursor.fetchall()

        return [
            {
                "id": todo[0],
                "title": todo[1],
                "description": todo[2],
                "priority": todo[3],
                "completed": bool(todo[4]),
                "due_date": todo[5],
                "created_at": todo[6],
                "updated_at": todo[7],
                "user_id": todo[8],
            }
            for todo in todos
        ]

    except sqlite3.Error as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        conn.close()


@app.post(
    "/todos",
    response_model=TodoResponse,
    status_code=201,
    summary="Create new todo",
    tags=["Todos"],
)
def create_todo(todo: TodoCreate):
    """Create a new todo item"""
    current_user = get_current_user()
    if not current_user:
        return {"error": "Authentication required"}, 401

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """INSERT INTO todos (title, description, priority, due_date, user_id)
               VALUES (?, ?, ?, ?, ?)""",
            (
                todo.title,
                todo.description,
                todo.priority,
                todo.due_date,
                current_user["user_id"],
            ),
        )
        todo_id = cursor.lastrowid
        conn.commit()

        # Fetch the created todo
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        created_todo = cursor.fetchone()

        return {
            "id": created_todo[0],
            "title": created_todo[1],
            "description": created_todo[2],
            "priority": created_todo[3],
            "completed": bool(created_todo[4]),
            "due_date": created_todo[5],
            "created_at": created_todo[6],
            "updated_at": created_todo[7],
            "user_id": created_todo[8],
        }, 201

    except sqlite3.Error as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        conn.close()


if __name__ == "__main__":
    # Initialize database
    init_db()

    print("🚀 Starting TODO API...")
    print("📚 Documentation: http://127.0.0.1:8000/docs")
    print("🔐 Authentication required for most endpoints")
    print("📝 Register at: POST /auth/register")
    print("🔑 Login at: POST /auth/login")

    app.run(host="127.0.0.1", port=8000, debug=True)
