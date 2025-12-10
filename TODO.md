# BustAPI Roadmap & TODO

This document tracks features that are currently missing, incomplete, or planned for future releases of BustAPI.

## 🚧 Incomplete / Work in Progress

### 1. File Upload Support (`multipart/form-data`)

- [x] **Rust Backend**: Implement `multipart` parsing in `src/`. Currently, only JSON and URL-encoded forms are parsed.
- [x] **Python API**: Implement `request.files` to populate from the parsed Rust data.
- [x] **Storage**: Add helpers for saving uploaded files (e.g., `file.save/save_to`).

### 2. Advanced Path Parameters (`Path`)

- [ ] **Validation**: Add `Path()` helper (similar to Pydantic/FastAPI) to validate route parameters (min/max length, regex, etc.).
- [ ] **Auto-Docs**: Integrate `Path` metadata into the auto-generated documentation.

## 🔮 Missing Features (Planned)

### 3. Request Validation & Dependency Injection

- [ ] **Query/Body**: `Query()`, `Body()` helpers for strict type validation.
- [ ] **Dependency Injection**: System for `Depends()` to handle auth and database sessions cleanly.

### 4. WebSockets

- [ ] **Core**: Add WebSocket upgrade support in Rust (Actix-web supports it, needs binding).
- [ ] **API**: Python `websocket` endpoint wrapper.

### 5. Background Tasks

- [ ] **Async Tasks**: Simple background task runner (fire-and-forget) after response is sent.

### 6. Middleware Improvements

- [ ] **CORS**: Built-in CORS middleware (currently manual or missing).
- [ ] **GZip**: Compression middleware.

### 7. Cookies

- [ ] **Request Cookies**: `request.cookies` is currently manually parsed from headers in Python. Move parsing to Rust for performance.
- [ ] **Response Cookies**: Unified `response.set_cookie` API is basic.

## 🐛 Known Issues / Technical Debt

- **Error Handling**: Rust panics in some edge cases (e.g. bad headers) should bubble up as Python exceptions.
- **Testing**: Need more comprehensive integration tests for the Rust-Python boundary.
