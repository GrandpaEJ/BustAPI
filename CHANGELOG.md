# Changelog

All notable changes to this project will be documented here.

## [0.2.2] - 2024-12-10

### Added

- **Comprehensive Examples**: Added examples for Templates (`05_templates.py`), Blueprints (`06_blueprints.py`), Database (`07_database_raw.py`), Auto-docs (`08_auto_docs.py`), and Complex Routing (`09_complex_routing.py`).
- **Automated Benchmarks**: New `benchmarks/run_comparison_auto.py` with CPU/RAM monitoring and device info capture.
- **Documentation**: Expanded documentation structure with `mkdocs`, including User Guide and API Reference.
- **CI/CD Improvements**: Robust CI pipeline with `black`, `ruff`, and strict dependency management (`requests`, etc.).

### Fixed

- Fixed internal `Router` visibility for crate-level testing.
- Resolved CI build failures related to missing test files and dependencies.
- Fixed `ruff` import sorting errors and `clippy` warnings.

## [0.2.0] - 2024-12-05

### Changed

- **BREAKING**: Migrated from Hyper to Actix-web for 50x+ performance improvement
- Updated PyO3 from 0.20 to 0.23 with free-threading support
- Added `gil_used = false` annotation for Python 3.13 free-threaded mode
- Removed `spawn_blocking` - direct Python handler calls for parallel execution
- Server now uses Actix-web's built-in worker pool (auto-scales to CPU cores)

### Added

- Python 3.13 free-threaded mode support (no GIL bottleneck!)
- Expected 30k-100k+ RPS with dynamic Python handlers

## [0.1.5]

- Added Jinja2 templating helper and `render_template` API
- Added minimal OpenAPI JSON generator and `/openapi.json` endpoint
- CI: Make workflows platform-aware for virtualenv and maturin invocations
- CI: Flatten downloaded artifacts before PyPI publish

## [0.1.0]

- Initial release
