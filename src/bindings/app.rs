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
    template_env: crate::templating::TemplateEnv,
}

// Helper methods (not exposed to Python)
impl PyBustApp {
    /// Extract param types from Flask-style route pattern
    fn extract_param_types_from_pattern(
        pattern: &str,
    ) -> std::collections::HashMap<String, String> {
        let mut types = std::collections::HashMap::new();

        for part in pattern.split('/') {
            if part.starts_with('<') && part.ends_with('>') {
                let inner = &part[1..part.len() - 1];
                let (type_str, name) = if let Some((t, n)) = inner.split_once(':') {
                    (t.trim(), n.trim())
                } else {
                    ("str", inner.trim())
                };
                types.insert(name.to_string(), type_str.to_string());
            }
        }

        types
    }
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
            template_env: crate::templating::create_env(None),
        })
    }

    /// Configure template folder
    pub fn set_template_folder(&mut self, folder: String) {
        self.template_env = crate::templating::create_env(Some(folder));
    }

    /// Render a template using the valid JSON context string
    pub fn render_template(&self, template_name: String, context_json: String) -> PyResult<String> {
        let ctx: serde_json::Value = serde_json::from_str(&context_json).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Failed to parse context JSON: {}", e))
        })?;

        let tmpl = self
            .template_env
            .get_template(&template_name)
            .map_err(|e| {
                if e.kind() == minijinja::ErrorKind::TemplateNotFound {
                    pyo3::exceptions::PyFileNotFoundError::new_err(format!(
                        "Template '{}' not found",
                        template_name
                    ))
                } else {
                    pyo3::exceptions::PyValueError::new_err(format!(
                        "Error loading template '{}': {}",
                        template_name, e
                    ))
                }
            })?;

        tmpl.render(ctx).map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!(
                "Failed to render template '{}': {}",
                template_name, e
            ))
        })
    }

    /// Add a route with a Python handler
    /// Now with automatic Rust-side path param extraction!
    pub fn add_route(&self, method: &str, path: &str, handler: Py<PyAny>) -> PyResult<()> {
        // Parse param types from path pattern
        let param_types = Self::extract_param_types_from_pattern(path);

        let py_handler = if param_types.is_empty() {
            // No path params - use simple handler
            crate::bindings::handlers::PyRouteHandler::new(handler)
        } else {
            // Has path params - use pattern-aware handler
            crate::bindings::handlers::PyRouteHandler::with_pattern(
                handler,
                path.to_string(),
                param_types,
            )
        };

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

    /// Add a typed turbo route with path parameter extraction in Rust
    ///
    /// This is the fastest route type for dynamic paths.
    /// Parameters are parsed and converted in Rust before calling Python.
    ///
    /// Args:
    ///     method: HTTP method (GET, POST, etc.)
    ///     path: Route pattern with typed params (e.g., "/users/<int:id>")
    ///     handler: Python handler function
    ///     param_types: Dict mapping param name to type ("int", "float", "str")
    ///     cache_ttl: Optional cache TTL in seconds (0 = no caching)
    #[pyo3(signature = (method, path, handler, param_types, cache_ttl=0))]
    pub fn add_typed_turbo_route(
        &self,
        method: &str,
        path: &str,
        handler: Py<PyAny>,
        param_types: std::collections::HashMap<String, String>,
        cache_ttl: u64,
    ) -> PyResult<()> {
        let py_handler = crate::bindings::typed_turbo::PyTypedTurboHandler::with_cache(
            handler,
            path.to_string(),
            param_types,
            cache_ttl,
        );

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
    pub fn add_async_route(&self, method: &str, path: &str, handler: Py<PyAny>) -> PyResult<()> {
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

    /// Add a WebSocket route with a Python handler
    pub fn add_websocket_route(&self, path: &str, handler: Py<PyAny>) -> PyResult<()> {
        let state = self.state.clone();
        let path = path.to_string();

        self.runtime.block_on(async {
            let mut ws_handlers = state.websocket_handlers.write().await;
            ws_handlers.insert(path, handler);
        });

        Ok(())
    }

    /// Add a Turbo WebSocket route - pure Rust, maximum performance
    /// The response_prefix is prepended to each received message
    pub fn add_turbo_websocket_route(&self, path: &str, response_prefix: String) -> PyResult<()> {
        let handler = std::sync::Arc::new(crate::websocket::TurboWebSocketHandler::new(
            response_prefix,
        ));
        let state = self.state.clone();
        let path = path.to_string();

        self.runtime.block_on(async {
            let mut turbo_handlers = state.turbo_websocket_handlers.write().await;
            turbo_handlers.insert(path, handler);
        });

        Ok(())
    }
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
        let path = if path_prefix.ends_with('/') {
            format!("{}<path:subpath>", path_prefix)
        } else {
            format!("{}/<path:subpath>", path_prefix)
        };

        let state = self.state.clone();
        let method_enum = http::Method::GET;

        self.runtime.block_on(async {
            let mut routes = state.routes.write().await;
            routes.add_route(method_enum, path, handler);
        });

        Ok(())
    }

    /// Configure automatic trailing slash redirection
    pub fn set_redirect_slashes(&self, enabled: bool) -> PyResult<()> {
        let state = self.state.clone();
        self.runtime.block_on(async {
            let mut routes = state.routes.write().await;
            routes.redirect_slashes = enabled;
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
                .with_env_filter("debug,actix_server=error,actix_web=error,notify=error")
                .try_init();
        } else {
            // Clean mode: Suppress Actix startup noise
            let _ = tracing_subscriber::fmt()
                .with_env_filter("info,actix_server=error,actix_web=error")
                .try_init();
        }

        // In Python 3.13 free-threaded, we can release GIL and run full parallel!
        // In Python 3.13 free-threaded, we can release GIL and run full parallel!

        // Update debug state
        self.state
            .debug
            .store(debug, std::sync::atomic::Ordering::Relaxed);

        Python::attach(|py| {
            py.detach(|| {
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
