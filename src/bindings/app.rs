//! PyO3 bindings with Actix-web integration
//! Optimized for Python 3.13 free-threaded mode (no GIL bottleneck)

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyString, PyTuple};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::runtime::Runtime;

use crate::server::{AppState, FastRouteHandler, RouteHandler, ServerConfig};

/// Python wrapper for the BustAPI application
#[pyclass]
pub struct PyBustApp {
    state: Arc<AppState>,
    config: ServerConfig,
    runtime: Runtime,
}

#[pymethods]
impl PyBustApp {
    #[new]
    pub fn new() -> PyResult<Self> {
        // Create an optimized Tokio runtime for high performance
        let cpu_count = num_cpus::get();
        let runtime = tokio::runtime::Builder::new_multi_thread()
            .enable_all()
            .worker_threads(cpu_count)
            .max_blocking_threads(cpu_count * 4)
            .thread_name("bustapi-worker")
            .build()
            .map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(format!(
                    "Failed to create async runtime: {}",
                    e
                ))
            })?;

        Ok(Self {
            state: Arc::new(AppState::new()),
            config: ServerConfig::default(),
            runtime,
        })
    }

    /// Add a route with a Python handler
    pub fn add_route(&self, method: &str, path: &str, handler: PyObject) -> PyResult<()> {
        let py_handler = crate::bindings::handlers::PyRouteHandler::new(handler);

        // Use blocking task to add route
        let state = self.state.clone();
        let method = method.to_string();
        let path = path.to_string();

        self.runtime.block_on(async {
            let mut routes = state.routes.write().await;
            routes.add_route(&method, &path, py_handler);
        });

        Ok(())
    }

    /// Add an async route with a Python handler
    pub fn add_async_route(&self, method: &str, path: &str, handler: PyObject) -> PyResult<()> {
        let py_handler = crate::bindings::handlers::PyAsyncRouteHandler::new(handler);

        let state = self.state.clone();
        let method = method.to_string();
        let path = path.to_string();

        self.runtime.block_on(async {
            let mut routes = state.routes.write().await;
            routes.add_route(&method, &path, py_handler);
        });

        Ok(())
    }

    /// Add a fast Rust-only route (maximum performance, no Python)
    pub fn add_fast_route(
        &self,
        method: &str,
        path: &str,
        response_body: String,
    ) -> PyResult<()> {
        let fast_handler = FastRouteHandler::new(response_body);

        let state = self.state.clone();
        let method = method.to_string();
        let path = path.to_string();

        self.runtime.block_on(async {
            let mut routes = state.routes.write().await;
            routes.add_route(&method, &path, fast_handler);
        });

        Ok(())
    }

    /// Run the server
    pub fn run(&mut self, host: &str, port: u16) -> PyResult<()> {
        self.config.host = host.to_string();
        self.config.port = port;

        let config = self.config.clone();
        let state = self.state.clone();

        // Release the GIL while running the server
        Python::with_gil(|py| {
            py.allow_threads(|| {
                self.runtime.block_on(async {
                    crate::server::start_server(config, state).await
                })
            })
        })
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Server error: {}", e)))
    }
}