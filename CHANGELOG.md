# Changelog

All notable changes to this project will be documented here.

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

- Python 3.13 free-threaded mode support (no GIL bottleneck!)
- Expected 30k-100k+ RPS with dynamic Python handlers

## [0.1.5] - 2025-11-05

- Added Jinja2 templating helper and `render_template` API
- Added minimal OpenAPI JSON generator and `/openapi.json` endpoint
- CI: Make workflows platform-aware for virtualenv and maturin invocations
- CI: Flatten downloaded artifacts before PyPI publish

## [0.1.0] - 2025-10-05

- Initial release
