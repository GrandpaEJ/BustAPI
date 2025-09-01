#!/usr/bin/env python3
"""
FastAPI-style Auto Documentation Example

This example demonstrates automatic API documentation generation in BustAPI,
similar to FastAPI's OpenAPI/Swagger integration:
- Automatic OpenAPI schema generation
- Interactive Swagger UI
- ReDoc documentation
- Type hints and validation
- Request/response models
"""

from bustapi import BustAPI
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Create app with documentation enabled
app = BustAPI(
    title="BustAPI Auto Documentation Demo",
    description="A comprehensive example of automatic API documentation generation",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json"  # OpenAPI schema
)

# Pydantic models for request/response validation
class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    age: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int]
    is_active: bool
    created_at: datetime

class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int

# In-memory storage for demo
users_db = {
    1: User(id=1, name="Alice", email="alice@example.com", age=30, created_at=datetime.now()),
    2: User(id=2, name="Bob", email="bob@example.com", age=25, created_at=datetime.now()),
}
next_id = 3

@app.get("/", 
         summary="Root endpoint",
         description="Welcome message for the API",
         response_model=dict,
         tags=["General"])
def read_root():
    """
    Welcome endpoint that provides basic API information.
    
    Returns basic information about the API including available endpoints
    and documentation links.
    """
    return {
        "message": "Welcome to BustAPI Auto Documentation Demo!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json"
    }

@app.get("/users", 
         response_model=List[UserResponse],
         summary="Get all users",
         description="Retrieve a list of all users in the system",
         tags=["Users"])
def get_users(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
):
    """
    Get all users with optional pagination and filtering.
    
    - **skip**: Number of users to skip (for pagination)
    - **limit**: Maximum number of users to return
    - **active_only**: If true, only return active users
    """
    users = list(users_db.values())
    
    if active_only:
        users = [user for user in users if user.is_active]
    
    return users[skip:skip + limit]

@app.get("/users/{user_id}",
         response_model=UserResponse,
         summary="Get user by ID",
         description="Retrieve a specific user by their ID",
         responses={
             200: {"description": "User found", "model": UserResponse},
             404: {"description": "User not found", "model": ErrorResponse}
         },
         tags=["Users"])
def get_user(user_id: int):
    """
    Get a specific user by ID.
    
    - **user_id**: The ID of the user to retrieve
    
    Returns the user data if found, otherwise returns a 404 error.
    """
    if user_id not in users_db:
        return ErrorResponse(
            error="Not Found",
            message=f"User with ID {user_id} not found",
            status_code=404
        ), 404
    
    return users_db[user_id]

@app.post("/users",
          response_model=UserResponse,
          status_code=201,
          summary="Create new user",
          description="Create a new user in the system",
          responses={
              201: {"description": "User created successfully", "model": UserResponse},
              400: {"description": "Invalid user data", "model": ErrorResponse}
          },
          tags=["Users"])
def create_user(user: UserCreate):
    """
    Create a new user.
    
    - **name**: User's full name (required)
    - **email**: User's email address (required)
    - **age**: User's age (optional)
    
    Returns the created user with assigned ID and timestamp.
    """
    global next_id
    
    # Check if email already exists
    for existing_user in users_db.values():
        if existing_user.email == user.email:
            return ErrorResponse(
                error="Bad Request",
                message=f"User with email {user.email} already exists",
                status_code=400
            ), 400
    
    new_user = User(
        id=next_id,
        name=user.name,
        email=user.email,
        age=user.age,
        created_at=datetime.now()
    )
    
    users_db[next_id] = new_user
    next_id += 1
    
    return new_user

@app.put("/users/{user_id}",
         response_model=UserResponse,
         summary="Update user",
         description="Update an existing user's information",
         responses={
             200: {"description": "User updated successfully", "model": UserResponse},
             404: {"description": "User not found", "model": ErrorResponse}
         },
         tags=["Users"])
def update_user(user_id: int, user_update: UserUpdate):
    """
    Update an existing user.
    
    - **user_id**: The ID of the user to update
    - **name**: New name (optional)
    - **email**: New email (optional)
    - **age**: New age (optional)
    - **is_active**: New active status (optional)
    
    Only provided fields will be updated.
    """
    if user_id not in users_db:
        return ErrorResponse(
            error="Not Found",
            message=f"User with ID {user_id} not found",
            status_code=404
        ), 404
    
    user = users_db[user_id]
    
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.age is not None:
        user.age = user_update.age
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    return user

@app.delete("/users/{user_id}",
            summary="Delete user",
            description="Delete a user from the system",
            responses={
                200: {"description": "User deleted successfully"},
                404: {"description": "User not found", "model": ErrorResponse}
            },
            tags=["Users"])
def delete_user(user_id: int):
    """
    Delete a user by ID.
    
    - **user_id**: The ID of the user to delete
    
    Returns success message if user was deleted.
    """
    if user_id not in users_db:
        return ErrorResponse(
            error="Not Found",
            message=f"User with ID {user_id} not found",
            status_code=404
        ), 404
    
    deleted_user = users_db.pop(user_id)
    
    return {
        "message": f"User {deleted_user.name} deleted successfully",
        "deleted_user_id": user_id
    }

@app.get("/health",
         summary="Health check",
         description="Check if the API is running and healthy",
         tags=["System"])
def health_check():
    """
    Health check endpoint.
    
    Returns the current status of the API and basic system information.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_users": len(users_db),
        "active_users": len([u for u in users_db.values() if u.is_active])
    }

if __name__ == '__main__':
    print("🚀 Starting BustAPI Auto Documentation Demo...")
    print("\n📚 Documentation URLs:")
    print("   Swagger UI: http://127.0.0.1:8000/docs")
    print("   ReDoc:      http://127.0.0.1:8000/redoc")
    print("   OpenAPI:    http://127.0.0.1:8000/openapi.json")
    print("\n🔗 API Endpoints:")
    print("   GET    /users")
    print("   POST   /users")
    print("   GET    /users/{id}")
    print("   PUT    /users/{id}")
    print("   DELETE /users/{id}")
    print("   GET    /health")
    
    app.run(host='127.0.0.1', port=8000, debug=True)
