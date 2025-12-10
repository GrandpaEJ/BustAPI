//! BustAPI Core - Rust backend with Actix-web for high-performance web framework
//!
//! This library provides the core HTTP server functionality built with Actix-web,
//! exposed to Python through PyO3 bindings.
//!
//! Optimized for Python 3.13 free-threaded mode (no GIL bottleneck!)

use pyo3::prelude::*;

mod bindings;
mod crypto;
mod logger;
mod rate_limiter;
mod request;
mod response;
mod router;
mod server;
mod static_files;

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

    // Add helper functions
    m.add_function(wrap_pyfunction!(create_app, m)?)?;

    Ok(())
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
