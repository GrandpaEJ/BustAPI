# Changelog

All notable changes to this project will be documented here.

## [0.9.0] - 2026-01-22

### Major Features

- **WebSocket Support**:
  - Full WebSocket support with `@app.websocket()` decorator.
  - Integration with `actix-ws` for heavy lifting in Rust.
  - Python-side API compatible with popular async frameworks.

- **Turbo WebSocket (Performance)**:
  - New `@app.turbo_websocket()` decorator for ultra-high performance.
  - **Pure Rust Message Handling**: Messages are processed entirely in Rust (no Python GIL, no callbacks) for maximum throughput.
  - **~74% Performance Boost**: Benchmarks show ~17k msg/sec vs ~10k msg/sec for standard mode.

- **Video Streaming & Range Requests**:
  - Full support for HTTP `Range` requests (seeking, scrubbing) via `FileResponse` and static files.
  - Implemented `HEAD` method support for all routes to handle browser pre-flight checks correctly.
  - Video streaming is now production-ready (verified with browser tests).

- **Rust-Core Request Logging**:
  - Migrated logging logic from Python to Rust for 100% request coverage.
  - Now captures **404 Not Found**, **Static Files**, and **Fast Routes** which were previously invisible to Python middleware.
  - High-performance, zero-allocation logging with accurate Rust-level latency timings.
  - Removed duplicate logging hooks from Python side.

- **Rust-Based Path Parameter Extraction**:
  - Moved regex parsing and parameter extraction to the Rust backend.
  - Significant performance boost for dynamic routes.
  - Supports `int`, `float`, `path`, and strict validation rules entirely in Rust.

- **Developer Experience**:
  - Enhanced Hot-Reloader: Cleaner output, suppresses internal noise, and clearly shows changed files.
  - `bustapi.logging`: New customizable logging module for users.

### Added

- `src/websocket/mod.rs` and `session.rs` for core WebSocket logic.
- `src/websocket/turbo.rs` for optimized Rust-only handling.
- `examples/advanced/28_websocket.py` and `29_turbo_websocket.py`.
- `benchmarks/ws_benchmark.py` for testing WebSocket performance.

### Refactoring

- **Modular Application Structure**:
  - Refactored `app.py` into a Mixin-based architecture (`RoutingMixin`, `ExtractionMixin`, `ContextMixin`, `HooksMixin`) for better maintainability.
  - Improved WSGI/ASGI compatibility with `WSGIAdapter` mixin.

### Fixed

- **Static Route Registration**: Fixed a bug where static route patterns were generated without a leading slash.
- **Example Fixes**: Updated `27_video_stream.py` to correctly resolve static folders relative to the script directory.
- **Process Management**: Fixed a recursion bug in `kill_process` utility.

### Performance

- **Optimized Route Matching**: Deterministic scoring system and Rust-side optimizations.

### Fixed

- **Session Logout Bug**: Fixed issue where `session.pop()` failures to persist changes to the session cookie ([#17](https://github.com/GrandpaEJ/BustAPI/issues/17)).
- **Template Headers**: `render_template` now correctly returns an `HTMLResponse` ensuring `Content-Type: text/html` is set instead of relying on implicit string handling ([#17](https://github.com/GrandpaEJ/BustAPI/issues/17)).

## [0.8.0] - 2026-01-14

### Added

- **Typed Dynamic Turbo Routes**:
  - `@app.turbo_route()` now supports path parameters: `/users/<int:id>`.
  - Path parameters are parsed in Rust for maximum performance (~30k RPS).
  - Supports `int`, `float`, `str`, and `path` parameter types.
  - Automatic type validation with 404 response for mismatches.
  - Big integer support via Python fallback (no overflow).
  - Multiple parameters: `/posts/<int:id>/comments/<int:cid>`.

- **Turbo Routes Documentation**:
  - New `docs/user-guide/turbo-routes.md` with comprehensive guide.
  - Example `examples/turbo/typed_turbo_example.py`.

### Changed

- `turbo_route` decorator now auto-detects parameters from route pattern.
- Improved error responses with structured JSON for type mismatches.

### Fixed

- **Static File Serving**:
  - Fixed 404 errors for nested static files (e.g. `css/style.css`) using new wildcard routing.
  - **Robust Path Resolution**: Implemented `get_root_path` to correctly locate `templates` and `static` folders regardless of working directory.
- **Dependency Issues**:
  - Removed `robyn` dependency to eliminate build conflicts and simplify installation.
  - Ensured compatibility across diverse Linux environments.

### Performance

- Dynamic turbo routes: ~30,000 requests/sec (vs ~18,000 for regular routes).
- 65% improvement for simple lookup endpoints.

### 🚀 Major Performance Breakthrough (Operation Mach 5)

- **Native Multiprocessing (Linux)**:
  - Implemented `os.fork()` based process manager with `SO_REUSEPORT` load balancing.
  - **Result**: **97,376 RPS** for standard routes (up from ~25k).
  - Beat Sanic (41k) and BlackSheep (28k) by a massive margin.
  - Memory usage remains efficient (~152MB for 4 workers).

- **Cross-Platform Support (Issue #9)**:
  - New `python/bustapi/multiprocess.py` module.
  - New `ci-multiplatform.yml` for automated cross-platform testing with `oha` benchmarks.
  - **CI Benchmark Results:**
    - **Linux**: 55,726 RPS (CI runner) / 105,012 RPS (local)
    - **macOS**: 35,560 RPS (single-process)
    - **Windows**: 17,772 RPS (single-process)
  - Platform-specific behavior:
    - **Linux**: Full multiprocessing with `SO_REUSEPORT` (100k+ RPS)
    - **macOS/Windows**: Single-process fallback (Rust still 3x faster than Flask!)

- **Cached Turbo Routes**:
  - New built-in caching for turbo routes: `@app.turbo_route("/", cache_ttl=60)`.
  - **Result**: **~140,961 RPS** for cached endpoints.
  - Zero-latency responses (< 1ms).

---

## [0.7.0] - 2026-01-13

### Added

- **JWT Authentication (Rust-backed)**:
  - `JWT` class for token management with HS256/HS384/HS512 algorithms.
  - `create_access_token()` and `create_refresh_token()` methods.
  - `decode_token()` and `verify_token()` for validation.
  - Decorators: `@jwt_required`, `@jwt_optional`, `@fresh_jwt_required`, `@jwt_refresh_token_required`.
  - Custom claims support and configurable expiry times.

- **Session Login (Flask-Login style)**:
  - `LoginManager` - Configure user loading and session handling.
  - `login_user()` / `logout_user()` - Manage user sessions.
  - `current_user` proxy - Access logged-in user anywhere.
  - `BaseUser` / `AnonUser` - User model mixins.
  - `@login_required`, `@fresh_login_required` - Route protection.
  - `@roles_required`, `@permission_required` - Role-based access.

- **Password Hashing (Argon2id)**:
  - `hash_password()` - Secure password hashing using Argon2id (OWASP recommended).
  - `verify_password()` - Constant-time password verification.
  - PHC-formatted hashes with automatic salt generation.

- **Security Utilities**:
  - `generate_token()` - Cryptographically secure random token generation.
  - `generate_csrf_token()` - CSRF token generation (32 bytes, hex-encoded).
  - `CSRFProtect` class for automatic CSRF validation on forms.

- **New Dependencies** (Rust):
  - `jsonwebtoken` v9 for JWT encoding/decoding.
  - `argon2` v0.5 for password hashing.
  - `rand` v0.8 for secure random generation.

- **CLI Tool** (`bustapi`):
  - `bustapi new`: Scaffold new projects with `pip`, `uv`, or `poetry`.
  - `bustapi run`: Run development server with hot reload.
  - `bustapi routes`: List all registered routes.
  - `bustapi info`: View system and installation details.

- **Native Hot Reloading**: replaced `watchfiles` with a Rust-native watcher using the `notify` crate. This removes the `watchfiles` Python dependency and provides instant, low-overhead reloads

- **Advanced Routing**:
  - **Deterministic Matching**: Implemented scoring system (Exact > Typed > Generic > Wildcard) to resolve overlapping routes predictably.
  - **Wildcard Paths**: Added `<path:name>` type for matching multiple URL segments (e.g. for static files).

- **Examples**: `17_jwt_auth.py`, `18_session_login.py`.
- **Tests**: `test_jwt.py`, `test_auth.py`, `test_login_manager.py`.

- **Performance Optimizations**:
  - **Multiprocessing with SO_REUSEPORT**: Uses `os.fork()` to spawn multiple worker processes sharing the same port for true parallel scaling.
  - **Turbo Routes**: New `@app.turbo_route()` decorator for zero-overhead routing—skips request context, sessions, and middleware for simple handlers.
  - **mimalloc Allocator**: Rust backend uses mimalloc for faster memory allocation.
  - **Zero-Copy JSON**: Native Rust JSON serialization with `serde_json`, bypassing Python's `json.dumps()`.
  - **CPU-Specific Optimizations**: Build with `target-cpu=native` for maximum performance.

- **Python 3.14 Support** ([#8](https://github.com/GrandpaEJ/BustAPI/issues/8)):
  - Upgraded PyO3 from `0.23` to `0.27` to support Python 3.14.
  - Updated deprecated APIs: `Python::with_gil` → `Python::attach`, `PyObject` → `Py<PyAny>`, `downcast` → `cast`.

### Fixed

- **Static File Serving**:
  - Fixed 404 errors for nested static files (e.g. `css/style.css`) using new wildcard routing.
  - **Robust Path Resolution**: Implemented `get_root_path` to correctly locate `templates` and `static` folders regardless of working directory.

### Changed

- **Refactored `bustapi.auth`** into modular package: `auth/login.py`, `auth/user.py`, `auth/decorators.py`, `auth/password.py`, `auth/tokens.py`, `auth/csrf.py`.

## [0.6.0] - 2026-01-05

### Added

- **HTTP Range Support for Video Streaming**: Static files now support HTTP Range requests with `206 Partial Content` responses ([#1](https://github.com/GrandpaEJ/BustAPI/issues/1))
- **Strict Path Routing**: Bidirectional redirect support (FastAPI-style) ensures `/foo` and `/foo/` are both accessible, returning `307 Temporary Redirect` to the canonical URL ([#7](https://github.com/GrandpaEJ/BustAPI/issues/7))
- **Streaming Response Support**: Implemented `StreamingResponse` for efficiency streaming of content from sync and async iterators ([#3](https://github.com/GrandpaEJ/BustAPI/issues/3))
- **Async Request Body Support**: Added `await request.body()` and `async for chunk in request.stream()` methods for async compatibility ([#4](https://github.com/GrandpaEJ/BustAPI/issues/4))
- **Keyword Arguments Support**: Automatic injection of path and query parameters into handler keyword arguments ([#6](https://github.com/GrandpaEJ/BustAPI/issues/6))
- **Query Params Alias**: Added `request.query_params` property (alias to `request.args`) for FastAPI compatibility ([#5](https://github.com/GrandpaEJ/BustAPI/issues/5))
- **Flask-style `send_file` Helper**: Updated to return `FileResponse` for efficient file serving with Range support
- **Absolute Path Support**: `FileResponse` now automatically converts relative paths to absolute paths for flexible file serving
- Video streaming example (`examples/27_video_stream.py`) demonstrating static and dynamic video serving
- **Documentation**: Updated user guides for Routing, Responses (Streaming), and Request Data (Async Body).

### Removed

- **Manual File Serving Module** (`src/file_serving.rs`): Removed in favor of robust `actix-files` integration which handles Range requests automatically.

### Changed

- Refactored `src/server/handlers.rs` to use `actix-files` for serving file responses.
- Updated `src/bindings/converters.rs` to pass `FileResponse` and `StreamingResponse` objects directly to Rust backend.
- Updated `src/bindings/handlers.rs` to pass request headers to response converter.

### Fixed

- **Windows Support**: Gated Unix-specific hot-reload logic (`nix::unistd`) to fix build errors on Windows.
- **Jinja2**: Added `jinja2` as a core dependency to ensure `render_template` works out-of-the-box and fix CI test failures.
- **CI/CD**: Resolved Rust `clippy` checks for `manual_flatten` and `type_complexity` to ensure strict CI compliance.
- **Dynamic Route Range Support**: Dynamic routes returning `FileResponse` now correctly support Range requests (Video seeking/scrubbing).
- Improved memory efficiency for large file serving.

## [0.5.0] - 2026-01-01

### Major Features

- **FastAPI Compatibility Layer**:
  - Added support for `Header`, `Cookie`, `Form`, and `File` parameter validators.
  - Implemented `UploadFile` wrapper for easier file handling.
  - Added `BackgroundTasks` for simple background execution.
  - Introduced `JSONResponse`, `HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `FileResponse` aliases.

- **Core Context Improvements**:
  - Implemented functional `g` (application globals) and `current_app` context proxies.
  - Fixed issues where these globals were exported but not importable/functional.
  - Ensured correct context isolation using `contextvars`.

- **API Completeness**:
  - Improved `Request` object compatibility with Flask/Werkzeug (e.g. `request.files`, `request.cookies` via Rust).

## [0.4.0] - 2025-12-11

### Major Features

- **Dependency Injection System**: Full-featured `Depends()` support with recursive resolution.
  - Supports nested dependencies (dependency functions depending on other dependencies).
  - **Recursive Parameter Extraction**: Dependencies can define their own `Query`, `Path`, and `Body` parameters, which are automatically extracted from the request.
  - Async support: Dependencies can be sync or async functions.
  - Per-request caching and generator cleanup (dependency usage scope).
- **Body Validation**: Added `Body()` helper for JSON request body validation.
  - Support for dictionary and Pydantic-like validation.
  - Automatic type coercion and error handling (400 Bad Request).
  - Integration with static and dynamic routes.

### Performance

- **Benchmark Results**: Achieved **19,969 RPS** on root endpoint (benchmarked against Flask @ 4.7k and FastAPI @ 2.1k).
- **Optimized Dispatch**: Intelligent keyword argument filtering in dispatch wrappers prevents argument pollution while determining handler signatures at runtime.

### Fixed

- **Static Route Validations**: Fixed bug where static routes (fast path) skipped body and query parameter extraction.
- **TestClient**: Added proper `json` parameter support to `TestClient` methods for easier API testing.

- **Signature Errors**: Resolved "unexpected keyword argument" errors by filtering `kwargs` based on handler signatures.

### Added

- **Query Parameter Validation**: FastAPI-compatible `Query()` helper for query parameter validation
  - Type coercion: `str` → `int`, `float`, `bool`, `list`
  - All validation constraints: `ge`, `le`, `gt`, `lt`, `min_length`, `max_length`, `regex`
  - Required vs optional parameters with default values
  - OpenAPI schema generation with full constraint details
  - Example: `examples/23_query_validation.py`

### Performance

- **Cookie Parsing**: Moved cookie parsing from Python to Rust for 10-100x performance improvement
  - Request cookies now parsed in Rust with URL decoding
  - Zero Python overhead for cookie extraction

### Improved

- **Response Cookies**: Enhanced `Response.set_cookie()` API
  - URL encoding for cookie values (security)
  - Support for `datetime` objects and timestamps in `expires` parameter
  - SameSite validation (`Strict`, `Lax`, `None`)
  - Improved `delete_cookie()` with all cookie attributes for proper deletion
- **Path Documentation**: Integrated Path parameter metadata into OpenAPI documentation generator
  - Path constraints now visible in Swagger UI/ReDoc
  - Full OpenAPI 3.0 compliance

## [0.3.1] - 2025-12-10

### Improvements

- **Benchmark Suite**: Complete overhaul of `benchmarks/run_comparison_auto.py` to include FastAPI, detailed metrics (min/max latency, transfer rate), and "futuristic" reporting.
- **Python Compatibility**: Explicit support for Python 3.10 through 3.14 (experimental).

### Fixed

- **Reloader**: Fixed `watchfiles` integration on Linux by correctly serializing the subprocess command.
- **Linting**: Resolved `ruff` B904 error in `rate_limit.py` by properly chaining exceptions.

## [0.3.0] - 2025-12-10

### Major Changes

- **Codebase Refactoring**: Python codebase completely refactored into modular sub-packages (`bustapi.core`, `bustapi.http`, `bustapi.routing`, `bustapi.security`, etc.) for improved maintainability.
- **Documentation Overhaul**: Comprehensive documentation rewrite using MkDocs with "Beginner to Advanced" guides.
- **Security Enhancements**:
  - Rust-based Rate Limiter for high-performance request throttling.
  - Secure static file serving (blocking hidden files and path traversal).
  - `Security` extension for CORS and Security Headers.

### Added

- **New Examples**: `10_rate_limit_demo.py` showcasing the new rate limiter and logging.
- **Rust-based Logging**: High-performance, colorful request logging implemented in Rust.
- **User Experience**:
  - **Hot Reloading**: Enabled via `debug=True` or `reload=True` using `watchfiles`.
  - **ASGI/WSGI Support**: Run BustAPI with `uvicorn`, `gunicorn`, or `hypercorn` (e.g., `app.run(server='uvicorn')`).
  - **Benchmark Tools**: Built-in compatibility layer allows benchmarking against standard Python servers.

## [0.2.2] - 2025-12-10

### Added

- **Comprehensive Examples**: Added examples for Templates (`05_templates.py`), Blueprints (`06_blueprints.py`), Database (`07_database_raw.py`), Auto-docs (`08_auto_docs.py`), and Complex Routing (`09_complex_routing.py`).
- **Automated Benchmarks**: New `benchmarks/run_comparison_auto.py` with CPU/RAM monitoring and device info capture.
- **Documentation**: Expanded documentation structure with `mkdocs`, including User Guide and API Reference.
- **CI/CD Improvements**: Robust CI pipeline with `black`, `ruff`, and strict dependency management (`requests`, etc.).

### Fixed

- Fixed internal `Router` visibility for crate-level testing.
- Resolved CI build failures related to missing test files and dependencies.
- Fixed `ruff` import sorting errors and `clippy` warnings.

## [0.2.0] - 2025-12-05

### Changed

- **BREAKING**: Migrated from Hyper to Actix-web for 50x+ performance improvement
- Updated PyO3 from 0.20 to 0.23 with free-threading support
- Added `gil_used = false` annotation for Python 3.13 free-threaded mode
- Removed `spawn_blocking` - direct Python handler calls for parallel execution
- Server now uses Actix-web's built-in worker pool (auto-scales to CPU cores)

### Added


- Expected 30k-100k+ RPS with dynamic Python handlers

## [0.1.5] - 2025-11-05

- Added Jinja2 templating helper and `render_template` API
- Added minimal OpenAPI JSON generator and `/openapi.json` endpoint
- CI: Make workflows platform-aware for virtualenv and maturin invocations
- CI: Flatten downloaded artifacts before PyPI publish

## [0.1.0] - 2025-10-05

- Initial release
