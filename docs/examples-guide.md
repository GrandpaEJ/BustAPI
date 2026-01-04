# Examples Gallery

The `examples/` directory in the repository contains many complete scripts demonstrating BustAPI features. Here is a curated list.

## Basics

!!! note "Learning Path"
    Start here if you are new to web development or BustAPI.

- **01_hello_world.py**: The minimal application.
- **02_parameters.py**: How to use path parameters like `/user/<name>`.
- **03_async.py**: Using `async def` for non-blocking routes.
- **04_request_data.py**: accessing query args and form data.

## Data & Validation

Learn how to robustly handle input.

- **19_all_types.py**: Comprehensive demonstration of `Struct`, `Array`, `Integer`, etc.
- **21_path_validation.py**: Strict validation for path parameters.
- **23_query_validation.py**: Strict validation for query parameters.
- **24_body_and_depends.py**: Combining JSON bodies and Dependency Injection.

## Advanced Features

For production-grade applications.

- **06_blueprints.py**: Organizing your app into modules.
- **14_middleware.py**: Custom request/response hooks.
- **10_rate_limit_demo.py**: Using the built-in rate limiter to prevent abuse.
- **11_security_demo.py**: Implementing security headers.

## Database & Templates

- **05_templates.py**: Rendering Jinja2 templates.
- **07_database_raw.py**: Executing raw SQL queries.
- **10_database_sqlmodel.py**: Full integration with SQLModel (ORM).
