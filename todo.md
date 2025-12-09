# BustAPI Roadmap: Flask & FastAPI Compatibility

This document outlines the design and implementation steps required to achieve full compatibility with Flask and FastAPI, based on the current Rust backend (`src/*`).

## 1. Core Architecture Alignment

The current codebase has two router implementations: `src/server` (used by bindings) and `src/router` (unused but more feature-rich).

- [ ] **Unify Routing Logic**:
  - [ ] Integrate `src/router` (which supports middleware and better request/response structures) into `PyBustApp` (`src/bindings/app.rs`).
  - [ ] Replace `server::RouteStorage` with `router::Router`.
  - [ ] Ensure `PyRequest` and `PyResponse` map correctly to the unified router's data structures.

## 2. Flask Compatibility Layer

Flask relies heavily on thread-locals (or context-locals) and a specific lifecycle.

- [ ] **Context Locals (`request`, `g`, `session`)**:
  - [ ] Implement a mechanism in Rust to store request data in a task-local scope compatible with Python's `contextvars` (for async) or thread-locals (for sync).
  - [ ] Create Python-side proxies that resolve to these Rust-managed contexts.
- [ ] **Lifecycle Hooks**:
  - [ ] Add support for `before_request`, `after_request`, and `teardown_request`.
  - [ ] Implement these hooks in `src/router/middleware.rs` logic to ensure they run at the correct times.
- [ ] **Blueprints**:
  - [ ] Extend `PyBustApp` to support mounting "sub-routers" or Blueprint objects.
  - [ ] Update `router::Router` to handle prefixed routes and nested middleware.
- [ ] **Templating**:
  - [ ] While `Jinja2` is Python-side, ensure the generic `render_template` can access the globally set `request` context.
- [ ] **Error Handling**:
  - [ ] Implement global error handlers mapping Exception types to response handlers.

## 3. FastAPI Compatibility Layer

FastAPI features rely on Pydantic and type introspection.

- [ ] **Type Validation (Pydantic Integration)**:
  - [ ] Modify `PyRouteHandler` (`src/bindings/handlers.rs`) to inspect the Python handler's type hints.
  - [ ] Automatically parse JSON bodies into Pydantic models before calling the handler.
  - [ ] Helper function in Rust to run Pydantic validation efficiently.
- [ ] **Dependency Injection (`Depends`)**:
  - [ ] Implement a resolution system for dependencies in Rust (or hybrid Rust/Python) that runs before the main handler.
- [ ] **OpenAPI Generation**:
  - [ ] Expose route metadata (path, methods, input/output schemas) to Python to allow generation of `openapi.json`.
  - [ ] Store this metadata in the Rust `Router` struct for introspection.
- [ ] **APIRouter**:
  - [ ] Similar to Blueprints, implement `APIRouter` support for organizing routes.

## 4. Middleware System

- [ ] **Generic Middleware Support**:
  - [ ] Expose `Router::add_middleware` to Python.
  - [ ] Create a `PyMiddleware` wrapper allowing Python functions/classes to act as middleware (processing request/response).
  - [ ] Support both WSGI-style (Flask) and ASGI-style (FastAPI) middleware patterns where possible, or define a unified BustAPI middleware interface.

## 5. Request/Response Enhancements

- [ ] **Multipart/Form-Data**:
  - [ ] Add robust multipart parsing in `src/request` (using `multer` or similar Rust crate) to support file uploads (`request.files`).
- [ ] **Streaming Responses**:
  - [ ] Support streaming responses for large files or SSE (Server-Sent Events).
- [ ] **WebSockets**:
  - [ ] Add WebSocket upgrade support in `src/server` and expose handlers for it.

## 6. Testing & Benchmarking

- [ ] **Compliance Tests**:
  - [ ] Port standard Flask and FastAPI test suites to check for behavioral parity.
- [ ] **Performance Benchmarks**:
  - [ ] Ensure new compatibility layers (especially Pydantic validation) don't degrade the Rust performance benefits (aim for <10% overhead vs raw handler).

## 7. Python Wrapper Design (`py_wrapper`)

The Python layer (`bustapi` package) acts as the user-facing API, delegating heavy lifting to the Rust backend (`bustapi_core`).

- [ ] **BustAPI Class**:
  - [ ] Subclass or wrap `bustapi_core.PyBustApp`.
  - [ ] Implement `__init__` to accept configuration (similar to Flask/FastAPI).
  - [ ] Expose `route`, `get`, `post`, etc., decorators that register handlers with the Rust backend.
- [ ] **WSGI/ASGI Compatibility (Optional/Fallback)**:
  - [ ] **Native Runner Default**: `BustAPI.run()` MUST use the internal Rust/Actix server (`PyBustApp.run()`) by default for maximum performance.
  - [ ] **WSGI/ASGI Adaptors**: implementing `wsgi_app` or `asgi_app` should be a secondary priority, only for deployment in constrained environments where the native binary cannot run. Explicitly avoid Gunicorn/Uvicorn for the main performance path.
- [ ] **Minimal Dependencies**:
  - [ ] Avoid heavy Python frameworks like `werkzeug`, `starlette`, or `flask` as dependencies.
  - [ ] Keep the `bustapi` Python package lightweight, containing mostly type stubs and thin wrappers around the Rust core.
  - [ ] **Validation**: Use Pydantic V2 (Rust-core) for validation, or implement a lightweight Rust-based schema validator if Pydantic is too heavy.
- [ ] **Extension Interface**:
  - [ ] Create a `Flask`-compatible extension interface (`app.extensions`) to allow existing Flask plugins (like `Flask-SQLAlchemy`) to work (requires mocking `flask` module or patching).
