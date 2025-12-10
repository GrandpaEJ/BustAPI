//! PyO3 bindings with Actix-web integration
//! Optimized for Python 3.13 free-threaded mode (no GIL bottleneck)

use pyo3::prelude::*;
use std::sync::Arc;
use tokio::runtime::Runtime;

use crate::server::{start_server, AppState, FastRouteHandler, ServerConfig};

/// Python wrapper for the BustAPI application
#[pyclass]
pub struct PyBustApp {
    state: Arc<AppState>,
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
            runtime,
        })
    }

    /// Add a route with a Python handler
    pub fn add_route(&self, method: &str, path: &str, handler: PyObject) -> PyResult<()> {
        let py_handler = crate::bindings::handlers::PyRouteHandler::new(handler);

        // Use blocking task to add route
        let state = self.state.clone();
        let method_enum = std::str::FromStr::from_str(method)
            .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid HTTP method"))?;
        let path = path.to_string();

        self.runtime.block_on(async {
            let mut routes = state.routes.write().await;
            routes.add_route(method_enum, path, py_handler);
        });

        Ok(())
    }

    /// Add an async route with a Python handler
    pub fn add_async_route(&self, method: &str, path: &str, handler: PyObject) -> PyResult<()> {
        let py_handler = crate::bindings::handlers::PyAsyncRouteHandler::new(handler);

        let state = self.state.clone();
        let method_enum = std::str::FromStr::from_str(method)
            .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid HTTP method"))?;
        let path = path.to_string();

        self.runtime.block_on(async {
            let mut routes = state.routes.write().await;
            routes.add_route(method_enum, path, py_handler);
        });

        Ok(())
    }

    /// Add a fast Rust-only route (maximum performance, no Python)
    pub fn add_fast_route(&self, method: &str, path: &str, response_body: String) -> PyResult<()> {
        let fast_handler = FastRouteHandler::new(response_body);

        let state = self.state.clone();
        let method_enum = std::str::FromStr::from_str(method)
            .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid HTTP method"))?;
        let path = path.to_string();

        self.runtime.block_on(async {
            let mut routes = state.routes.write().await;
            routes.add_route(method_enum, path, fast_handler);
        });

        Ok(())
    }

    /// Add a secure static file route
    pub fn add_static_route(&self, path_prefix: &str, static_folder: &str) -> PyResult<()> {
        let handler = crate::static_files::StaticFileHandler::new(static_folder, path_prefix);
        let path = format!("{}<path>", path_prefix); // Dynamic match for /static/<path>

        let state = self.state.clone();
        let method_enum = http::Method::GET;

        self.runtime.block_on(async {
            let mut routes = state.routes.write().await;
            routes.add_route(method_enum, path, handler);
        });

        Ok(())
    }

    /// Run the server
    pub fn run(&self, host: String, port: u16, workers: usize, debug: bool) -> PyResult<()> {
        let state = self.state.clone();
        let config = ServerConfig {
            host,
            port,
            debug,
            workers,
        };

        // Initialize logging if debug is on and not already initialized
        if debug {
            // Debug mode: Show debug logs but suppress framework noise
            let _ = tracing_subscriber::fmt()
                .with_env_filter("debug,actix_server=error,actix_web=error")
                .try_init();
        } else {
            // Clean mode: Suppress Actix startup noise
            let _ = tracing_subscriber::fmt()
                .with_env_filter("info,actix_server=error,actix_web=error")
                .try_init();
        }

        // In Python 3.13 free-threaded, we can release GIL and run full parallel!
        // In Python 3.13 free-threaded, we can release GIL and run full parallel!
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let sys = actix_rt::System::new();
                sys.block_on(start_server(config, state))
            })
        })
        .map_err(|e| pyo3::exceptions::PyOSError::new_err(format!("Server error: {}", e)))?;

        Ok(())
    }
    /// Handle a request directly (for ASGI/WSGI support)
    /// Returns (body, status_code, headers)
    pub fn handle_request(
        &self,
        method: &str,
        path: &str,
        query_string: &str,
        headers: std::collections::HashMap<String, String>,
        body: Vec<u8>,
    ) -> PyResult<(String, u16, std::collections::HashMap<String, String>)> {
        let state = self.state.clone();
        let method_enum = std::str::FromStr::from_str(method)
            .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid HTTP method"))?;
        let path_string = path.to_string();
        let query_string = query_string.to_string();

        let mut req_data = crate::request::RequestData::new(method_enum, path_string);
        req_data.query_string = query_string;
        req_data.headers = headers;
        req_data.body = body;
        // Parse query params from query string if needed
        if !req_data.query_string.is_empty() {
            req_data.query_params = url::form_urlencoded::parse(req_data.query_string.as_bytes())
                .into_owned()
                .collect();
        }

        // We needs to block on the async runtime to acquire the lock and process
        // Since we are likely called from a sync context (WSGI) or async (ASGI via thread),
        // we use the runtime to execute.
        let response_data = self.runtime.block_on(async {
            let routes = state.routes.read().await;
            routes.process_request(req_data)
        });

        let body_str = response_data
            .body_as_string()
            .unwrap_or_else(|_| String::from_utf8_lossy(&response_data.body).to_string());

        Ok((
            body_str,
            response_data.status.as_u16(),
            response_data.headers,
        ))
    }
}
