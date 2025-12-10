# Release Track & Roadmap

## Release Track

BustAPI follows semver.

| Version    | Status   | Release Date | Highlights                                          |
| :--------- | :------- | :----------- | :-------------------------------------------------- |
| **v0.3.1** | 🟡 Beta  | 2025-12-10   | Bug fixes, Benchmark overhaul, Python 3.14 support  |
| **v0.3.0** | 🟡 Beta  | 2025-12-10   | Hot Reload, ASGI/WSGI Support, Security, Rate Limit |
| **v0.2.2** | 🟡 Beta  | 2025-12-10   | Comprehensive Examples, Auto-Benchmarks, Full Docs  |
| **v0.2.0** | 🟡 Beta  | 2025-12-05   | Migration to Actix-web, Free-threading Support      |
| **v0.1.5** | ⚪ Alpha | 2025-09-01   | Jinja2, OpenAPI, CI/CD Basics                       |
| **v0.1.0** | ⚪ Alpha | 2025-08-29   | Initial Proof of Concept                            |

## Roadmap

### v0.4.0 - The Ecosystem Update

- [ ] **ORM Support**: Native integration with SQLAlchemy or similar.
- [ ] **Middleware Overhaul**: Enhanced middleware system with better ordering and context.
- [ ] **Session Management**: Built-in session support.

### v0.5.0 - Performance Tuning

- [ ] **Zero-Copy Optimizations**: Further minimize copying between Rust and Python.
- [ ] **WebSockets**: Native WebSocket support via Actix.

### v1.0.0 - Production Ready

- [ ] **Full API Stability**: Frozen public API.
- [ ] **Security Audits**: Comprehensive security review.
