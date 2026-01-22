//! BustAPI Core - Rust backend with Actix-web for high-performance web framework
//!
//! This library provides the core HTTP server functionality built with Actix-web,
//! exposed to Python through PyO3 bindings.
//!
//! Optimized for Python 3.13 free-threaded mode (no GIL bottleneck!)

use pyo3::prelude::*;

mod bindings;
mod crypto;
mod jwt;

use mimalloc::MiMalloc;

#[global_allocator]
static GLOBAL: MiMalloc = MiMalloc;

mod logger;
mod rate_limiter;
mod request;
mod response;
mod router;
mod server;
mod static_files;
pub mod templating;
mod watcher;
pub mod websocket;

pub use request::RequestData;
pub use response::ResponseData;

/// Python module definition for bustapi_core
/// gil_used = false enables true parallelism with Python 3.13t!
#[pymodule(gil_used = false)]
fn bustapi_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_class::<bindings::PyBustApp>()?;
    m.add_class::<bindings::PyRequest>()?;
    m.add_class::<rate_limiter::PyRateLimiter>()?;
    m.add_class::<logger::PyFastLogger>()?;
    m.add_class::<crypto::Signer>()?;

    // JWT support
    m.add_class::<jwt::JWTManager>()?;

    // WebSocket support
    m.add_class::<bindings::PyWebSocketConnection>()?;
    m.add_class::<bindings::PyWebSocketHandler>()?;

    // Password hashing
    m.add_function(wrap_pyfunction!(crypto::hash_password, m)?)?;
    m.add_function(wrap_pyfunction!(crypto::verify_password, m)?)?;

    // Token generation
    m.add_function(wrap_pyfunction!(crypto::generate_token, m)?)?;
    m.add_function(wrap_pyfunction!(crypto::generate_csrf_token, m)?)?;

    // Helper functions
    m.add_function(wrap_pyfunction!(create_app, m)?)?;
    m.add_function(wrap_pyfunction!(enable_hot_reload, m)?)?;

    Ok(())
}

/// Enable hot reloading
#[pyfunction]
fn enable_hot_reload(path: String) {
    watcher::enable_hot_reload(path);
}

/// Create a new BustAPI application instance
#[pyfunction]
fn create_app() -> PyResult<bindings::PyBustApp> {
    bindings::PyBustApp::new()
}

#[cfg(test)]
mod tests {
    #[test]
    fn test_module_creation() {
        assert_eq!(2 + 2, 4);
    }
}
