//! PyO3 bindings with Actix-web integration
//! Optimized for Python 3.13 free-threaded mode (no GIL bottleneck)

// Note: RequestData and ResponseData from crate are not used directly here
// as we use inline PyRequest struct
use crate::server::{AppState, FastRouteHandler, RouteHandler, ServerConfig};
use actix_web::{web, HttpRequest, HttpResponse};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyString, PyTuple};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::runtime::Runtime;

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
        let py_handler = PyRouteHandler::new(handler);
        
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
        let py_handler = PyAsyncRouteHandler::new(handler);
        
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

/// Python route handler - calls Python function for each request
/// With Python 3.13 free-threaded mode, no GIL bottleneck!
pub struct PyRouteHandler {
    handler: PyObject,
}

impl PyRouteHandler {
    pub fn new(handler: PyObject) -> Self {
        Self { handler }
    }
}

impl RouteHandler for PyRouteHandler {
    fn handle(&self, req: &HttpRequest, body: web::Bytes) -> HttpResponse {
        // With Python 3.13t, this runs in parallel without GIL blocking!
        Python::with_gil(|py| {
            // Create request data
            let py_req = create_py_request(py, req, &body);
            
            match py_req {
                Ok(py_req_obj) => {
                    // Call Python handler
                    match self.handler.call1(py, (py_req_obj,)) {
                        Ok(result) => convert_py_result_to_response(py, result),
                        Err(e) => {
                            tracing::error!("Python handler error: {:?}", e);
                            HttpResponse::InternalServerError()
                                .content_type("application/json")
                                .body(r#"{"error": "Handler error"}"#)
                        }
                    }
                }
                Err(e) => {
                    tracing::error!("Request creation error: {:?}", e);
                    HttpResponse::InternalServerError()
                        .content_type("application/json")
                        .body(r#"{"error": "Request error"}"#)
                }
            }
        })
    }
}

/// Async Python route handler
pub struct PyAsyncRouteHandler {
    handler: PyObject,
}

impl PyAsyncRouteHandler {
    pub fn new(handler: PyObject) -> Self {
        Self { handler }
    }
}

impl RouteHandler for PyAsyncRouteHandler {
    fn handle(&self, req: &HttpRequest, body: web::Bytes) -> HttpResponse {
        // For async handlers, call and check if coroutine
        Python::with_gil(|py| {
            let py_req = create_py_request(py, req, &body);
            
            match py_req {
                Ok(py_req_obj) => {
                    match self.handler.call1(py, (py_req_obj,)) {
                        Ok(result) => {
                            // Check if coroutine
                            let asyncio = py.import("asyncio");
                            if let Ok(asyncio) = asyncio {
                                if let Ok(is_coro) = asyncio.call_method1("iscoroutine", (&result,)) {
                                    if is_coro.extract::<bool>().unwrap_or(false) {
                                        // Run coroutine
                                        if let Ok(loop_obj) = asyncio.call_method0("get_event_loop") {
                                            if let Ok(awaited) = loop_obj.call_method1("run_until_complete", (&result,)) {
                                                return convert_py_result_to_response(py, awaited.into());
                                            }
                                        }
                                    }
                                }
                            }
                            convert_py_result_to_response(py, result)
                        }
                        Err(e) => {
                            tracing::error!("Async handler error: {:?}", e);
                            HttpResponse::InternalServerError()
                                .content_type("application/json")
                                .body(r#"{"error": "Async handler error"}"#)
                        }
                    }
                }
                Err(e) => {
                    tracing::error!("Request creation error: {:?}", e);
                    HttpResponse::InternalServerError()
                        .content_type("application/json")
                        .body(r#"{"error": "Request error"}"#)
                }
            }
        })
    }
}

/// Python wrapper for HTTP requests
#[pyclass]
pub struct PyRequest {
    method: String,
    path: String,
    query_string: String,
    headers: HashMap<String, String>,
    body: Vec<u8>,
}

#[pymethods]
impl PyRequest {
    #[getter]
    pub fn method(&self) -> &str {
        &self.method
    }

    #[getter]
    pub fn path(&self) -> &str {
        &self.path
    }

    #[getter]
    pub fn query_string(&self) -> &str {
        &self.query_string
    }

    #[getter]
    pub fn headers(&self) -> HashMap<String, String> {
        self.headers.clone()
    }

    pub fn get_data(&self) -> &[u8] {
        &self.body
    }

    pub fn json(&self, py: Python) -> PyResult<PyObject> {
        let json_str = String::from_utf8_lossy(&self.body);
        if json_str.is_empty() {
            return Ok(py.None());
        }

        // Use serde_json for fast parsing
        match serde_json::from_str::<serde_json::Value>(&json_str) {
            Ok(value) => json_value_to_python(py, &value),
            Err(_) => {
                let json_module = py.import("json")?;
                let result = json_module.call_method1("loads", (json_str.to_string(),))?;
                Ok(result.into())
            }
        }
    }
}

/// Create PyRequest from Actix HttpRequest
fn create_py_request(py: Python, req: &HttpRequest, body: &web::Bytes) -> PyResult<Py<PyRequest>> {
    let mut headers = HashMap::new();
    for (key, value) in req.headers() {
        if let Ok(v) = value.to_str() {
            headers.insert(key.to_string(), v.to_string());
        }
    }

    let py_req = PyRequest {
        method: req.method().to_string(),
        path: req.path().to_string(),
        query_string: req.query_string().to_string(),
        headers,
        body: body.to_vec(),
    };

    Py::new(py, py_req)
}

/// Convert Python result to HttpResponse
fn convert_py_result_to_response(py: Python, result: PyObject) -> HttpResponse {
    // Check if tuple (body, status) or (body, status, headers)
    if let Ok(tuple) = result.downcast_bound::<PyTuple>(py) {
        match tuple.len() {
            2 => {
                if let (Ok(body), Ok(status)) = (
                    tuple.get_item(0),
                    tuple.get_item(1).and_then(|s| s.extract::<u16>()),
                ) {
                    let response_body = python_to_response_body(py, body.into());
                    return HttpResponse::build(
                        actix_web::http::StatusCode::from_u16(status)
                            .unwrap_or(actix_web::http::StatusCode::OK),
                    )
                    .content_type("application/json")
                    .body(response_body);
                }
            }
            3 => {
                if let (Ok(body), Ok(status), Ok(hdrs)) = (
                    tuple.get_item(0),
                    tuple.get_item(1).and_then(|s| s.extract::<u16>()),
                    tuple.get_item(2).and_then(|h| h.extract::<HashMap<String, String>>()),
                ) {
                    let response_body = python_to_response_body(py, body.into());
                    let status_code = actix_web::http::StatusCode::from_u16(status)
                        .unwrap_or(actix_web::http::StatusCode::OK);

                    let mut response = HttpResponse::build(status_code);
                    let mut content_type = "application/json";

                    // Set headers
                    for (k, v) in &hdrs {
                        if k.to_lowercase() == "content-type" {
                            content_type = v;
                        }
                        response.insert_header((k.as_str(), v.as_str()));
                    }

                    return response
                        .content_type(content_type)
                        .body(response_body);
                }
            }
            _ => {}
        }
    }

    // Default: treat as response body
    let body = python_to_response_body(py, result);

    // Check if body looks like HTML
    let content_type = if body.trim().starts_with("<") && body.contains("</") {
        "text/html; charset=utf-8"
    } else {
        "application/json"
    };

    HttpResponse::Ok()
        .content_type(content_type)
        .body(body)
}

/// Convert Python object to response body bytes
fn python_to_response_body(py: Python, obj: PyObject) -> String {
    if let Ok(bytes) = obj.downcast_bound::<PyBytes>(py) {
        return String::from_utf8_lossy(bytes.as_bytes()).to_string();
    }
    
    if let Ok(string) = obj.downcast_bound::<PyString>(py) {
        return string.to_string();
    }

    // Try JSON serialization
    if let Ok(json_module) = py.import("json") {
        if let Ok(json_str) = json_module.call_method1("dumps", (&obj,)) {
            if let Ok(s) = json_str.extract::<String>() {
                return s;
            }
        }
    }

    "{}".to_string()
}

/// Convert serde_json::Value to Python object using ToPyObject trait
fn json_value_to_python(py: Python, value: &serde_json::Value) -> PyResult<PyObject> {
    use pyo3::ToPyObject;
    
    match value {
        serde_json::Value::Null => Ok(py.None()),
        serde_json::Value::Bool(b) => Ok(b.to_object(py)),
        serde_json::Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.to_object(py))
            } else if let Some(f) = n.as_f64() {
                Ok(f.to_object(py))
            } else {
                Ok(py.None())
            }
        }
        serde_json::Value::String(s) => Ok(s.to_object(py)),
        serde_json::Value::Array(arr) => {
            let py_list = pyo3::types::PyList::empty(py);
            for item in arr {
                py_list.append(json_value_to_python(py, item)?)?;
            }
            Ok(py_list.to_object(py))
        }
        serde_json::Value::Object(obj) => {
            let py_dict = PyDict::new(py);
            for (key, val) in obj {
                py_dict.set_item(key, json_value_to_python(py, val)?)?;
            }
            Ok(py_dict.to_object(py))
        }
    }
}
