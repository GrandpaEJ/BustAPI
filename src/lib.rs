//! BustAPI Core - Rust backend for high-performance Flask-compatible web framework
//!
//! This library provides the core HTTP server functionality built with Tokio and Hyper,
//! exposed to Python through PyO3 bindings.

use pyo3::prelude::*;

mod bindings;
mod request;
mod response;
mod router;
mod server;

pub use request::RequestData;
pub use response::ResponseData;
pub use router::{RouteHandler, Router};
pub use server::BustServer;

/// Python module definition for bustapi_core
#[pymodule]
fn bustapi_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add("__version__", "0.1.0")?;
    m.add_class::<bindings::PyBustApp>()?;
    m.add_class::<bindings::PyRequest>()?;
    m.add_class::<bindings::PyResponse>()?;

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
        // Basic test to ensure module compiles
        assert_eq!(2 + 2, 4);
    }
}
