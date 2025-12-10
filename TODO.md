# BustAPI Roadmap & TODO

This document tracks features that are currently missing, incomplete, or planned for future releases of BustAPI.

## 🚧 Incomplete / Work in Progress

### 1. File Upload Support (`multipart/form-data`)

- [x] **Rust Backend**: Implement `multipart` parsing in `src/`. Currently, only JSON and URL-encoded forms are parsed.
- [x] **Python API**: Implement `request.files` to populate from the parsed Rust data.
- [x] **Storage**: Add helpers for saving uploaded files (e.g., `file.save/save_to`).

### 2. Advanced Path Parameters (`Path`)

- [x] **Validation**: Add `Path()` helper (similar to Pydantic/FastAPI) to validate route parameters (min/max length, regex, etc.).
- [x] **Auto-Docs**: Integrate `Path` metadata into the auto-generated documentation.

**Note**: Path validation is fully implemented and FastAPI-compatible. The `Path()` helper supports:

- Numeric constraints: `ge`, `le`, `gt`, `lt`
- String constraints: `min_length`, `max_length`, `regex`
- Documentation fields: `description`, `title`, `example`, `examples`, `alias`, `deprecated`
- OpenAPI schema generation with full constraint details

See `examples/21_path_validation.py` for validation examples and `examples/22_path_docs.py` for documentation examples.

## 🔮 Missing Features (Planned)

### 3. Request Validation & Dependency Injection

- [x] **Query/Body**: `Query()` helper implemented with strict type validation and coercion.
  - Type coercion: str → int, float, bool, list
  - All validation constraints from Path (ge, le, gt, lt, min_length, max_length, regex)
  - Required vs optional parameters with defaults
  - OpenAPI schema generation
  - See `examples/23_query_validation.py`
- [ ] **Body**: `Body()` helper for request body validation (JSON).
- [ ] **Dependency Injection**: System for `Depends()` to handle auth and database sessions cleanly.

### 4. WebSockets

- [ ] **Core**: Add WebSocket upgrade support in Rust (Actix-web supports it, needs binding).
- [ ] **API**: Python `websocket` endpoint wrapper.

### 5. Background Tasks

- [ ] **Async Tasks**: Simple background task runner (fire-and-forget) after response is sent.

### 6. Middleware Improvements

- [ ] **CORS**: Built-in CORS middleware (currently manual or missing).
- [ ] **GZip**: Compression middleware.

### 5. Cookies

- [x] **Request Cookies**: `request.cookies` now uses Rust parsing for high performance with URL decoding.
- [x] **Response Cookies**: Enhanced `response.set_cookie()` API with:
  - URL encoding for cookie values
  - Support for datetime objects in `expires` parameter
  - SameSite validation ('Strict', 'Lax', 'None')
  - Improved `delete_cookie()` with all cookie attributes

## 🐛 Known Issues / Technical Debt

- **Error Handling**: Rust panics in some edge cases (e.g. bad headers) should bubble up as Python exceptions.
- **Testing**: Need more comprehensive integration tests for the Rust-Python boundary.
