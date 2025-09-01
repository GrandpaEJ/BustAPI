//! PyO3 bindings to expose Rust functionality to Python
#![allow(non_local_definitions)]

use crate::request::RequestData;
use crate::response::ResponseData;
use crate::router::RouteHandler;
use crate::server::{BustServer, ServerConfig};
use async_trait::async_trait;
use http::Method;
use hyper::StatusCode;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyString, PyDict};
use pyo3_asyncio::tokio as pyo3_tokio;
use std::collections::HashMap;
use std::str::FromStr;
use std::sync::{Arc, Mutex};
use tokio::runtime::Runtime;

/// Python wrapper for the BustAPI application
#[pyclass]
pub struct PyBustApp {
    server: BustServer,
    runtime: Runtime,
}

#[allow(non_local_definitions)]
#[pymethods]
impl PyBustApp {
    #[new]
    pub fn new() -> PyResult<Self> {
        // Create an optimized Tokio runtime for high performance
        let cpu_count = num_cpus::get();
        let runtime = tokio::runtime::Builder::new_multi_thread()
            .enable_all()
            .worker_threads(cpu_count) // Use all available CPU cores
            .max_blocking_threads(cpu_count * 4) // More blocking threads for Python GIL
            .thread_name("bustapi-worker")
            .build()
            .map_err(|e| {
                PyRuntimeError::new_err(format!("Failed to create async runtime: {}", e))
            })?;

        Ok(Self {
            server: BustServer::new(),
            runtime,
        })
    }

    /// Add a route to the application
    pub fn add_route(&mut self, method: &str, path: &str, handler: PyObject) -> PyResult<()> {
        let method = Method::from_str(method)
            .map_err(|e| PyRuntimeError::new_err(format!("Invalid HTTP method: {}", e)))?;

        let py_handler = PyRouteHandler::new(handler);
        self.server
            .router_mut()
            .add_route(method, path.to_string(), py_handler);

        Ok(())
    }

    /// Add an async route to the application
    pub fn add_async_route(&mut self, method: &str, path: &str, handler: PyObject) -> PyResult<()> {
        let method = Method::from_str(method)
            .map_err(|e| PyRuntimeError::new_err(format!("Invalid HTTP method: {}", e)))?;

        let async_handler = PyAsyncRouteHandler::new(handler);
        self.server
            .router_mut()
            .add_route(method, path.to_string(), async_handler);

        Ok(())
    }

    /// Run the server synchronously
    pub fn run(&mut self, host: &str, port: u16) -> PyResult<()> {
        // Configure the server with host and port
        self.server.set_config(ServerConfig {
            host: host.to_string(),
            port,
            debug: false,
        });

        // Release the GIL while running the async server loop to avoid deadlock
        let result = Python::with_gil(|py| {
            py.allow_threads(|| self.runtime.block_on(async { self.server.serve().await }))
        });

        result.map_err(|e| PyRuntimeError::new_err(format!("Server error: {}", e)))
    }

    /// Run the server asynchronously (simplified for now)
    pub fn run_async(&mut self, host: &str, port: u16) -> PyResult<()> {
        // For now, just call the sync version
        // TODO: Implement proper async interface
        self.run(host, port)
    }

    /// Add a fast Rust-only route for testing maximum performance
    pub fn add_fast_route(&mut self, method: &str, path: &str, response_body: String) -> PyResult<()> {
        let method = Method::from_str(method)
            .map_err(|e| PyRuntimeError::new_err(format!("Invalid HTTP method: {}", e)))?;

        let fast_handler = FastRouteHandler::new(response_body);
        self.server
            .router_mut()
            .add_route(method, path.to_string(), fast_handler);

        Ok(())
    }
}

/// Python wrapper for HTTP requests
#[pyclass]
pub struct PyRequest {
    data: RequestData,
}

#[pymethods]
impl PyRequest {
    /// Get HTTP method
    #[getter]
    pub fn method(&self) -> &str {
        self.data.method_str()
    }

    /// Get request path
    #[getter]
    pub fn path(&self) -> &str {
        &self.data.path
    }

    /// Get query string
    #[getter]
    pub fn query_string(&self) -> &str {
        &self.data.query_string
    }

    /// Get request headers as dictionary
    #[getter]
    pub fn headers(&self) -> PyResult<HashMap<String, String>> {
        Ok(self.data.headers.clone())
    }

    /// Get query parameters as dictionary
    #[getter]
    pub fn args(&self) -> PyResult<HashMap<String, String>> {
        Ok(self.data.query_params.clone())
    }

    /// Get request body as bytes
    pub fn get_data(&self) -> &[u8] {
        &self.data.body
    }

    /// Get request body as string
    pub fn body_as_string(&self) -> PyResult<String> {
        self.data
            .body_as_string()
            .map_err(|e| PyRuntimeError::new_err(format!("Invalid UTF-8: {}", e)))
    }

    /// Get request body as JSON (optimized)
    pub fn json(&self, py: Python) -> PyResult<PyObject> {
        let json_str = self.body_as_string()?;
        if json_str.is_empty() {
            return Ok(py.None());
        }

        // Use serde_json for faster parsing, then convert to Python
        match serde_json::from_str::<serde_json::Value>(&json_str) {
            Ok(value) => {
                // Convert serde_json::Value to Python object more efficiently
                json_value_to_python(py, &value)
            }
            Err(_) => {
                // Fallback to Python json module if serde fails
                let json_module = py.import("json")?;
                let result = json_module.call_method1("loads", (json_str,))?;
                Ok(result.into())
            }
        }
    }

    /// Get form data
    pub fn form(&self) -> HashMap<String, String> {
        self.data.parse_form_data()
    }

    /// Get cookies
    pub fn cookies(&self) -> HashMap<String, String> {
        self.data.get_cookies()
    }

    /// Check if request is JSON
    pub fn is_json(&self) -> bool {
        self.data.is_json()
    }

    /// Get specific header value
    pub fn get_header(&self, name: &str) -> Option<String> {
        self.data.get_header(name).cloned()
    }
}

impl PyRequest {
    pub fn from_request_data(data: RequestData) -> Self {
        Self { data }
    }
}

/// Python wrapper for HTTP responses
#[pyclass]
pub struct PyResponse {
    pub data: ResponseData,
}

#[allow(non_local_definitions)]
#[pymethods]
impl PyResponse {
    #[new]
    pub fn new(
        response: Option<PyObject>,
        status: Option<u16>,
        headers: Option<HashMap<String, String>>,
    ) -> PyResult<Self> {
        let mut resp_data = ResponseData::new();

        // Set status if provided
        if let Some(status_code) = status {
            resp_data.status = StatusCode::from_u16(status_code)
                .map_err(|e| PyRuntimeError::new_err(format!("Invalid status code: {}", e)))?;
        }

        // Set headers if provided
        if let Some(headers_map) = headers {
            resp_data.headers = headers_map;
        }

        // Set body if provided
        if let Some(response_obj) = response {
            Python::with_gil(|py| {
                if let Ok(bytes) = response_obj.downcast::<PyBytes>(py) {
                    resp_data.body = bytes.as_bytes().to_vec();
                } else if let Ok(string) = response_obj.downcast::<PyString>(py) {
                    resp_data.body = string.to_string().into_bytes();
                } else {
                    // Try to convert to JSON
                    let json_module = py.import("json")?;
                    let json_str = json_module.call_method1("dumps", (response_obj,))?;
                    let json_string: String = json_str.extract()?;
                    resp_data.body = json_string.into_bytes();
                    resp_data.set_header("Content-Type", "application/json");
                }
                Ok::<(), PyErr>(())
            })?;
        }

        Ok(Self { data: resp_data })
    }

    /// Get response status code
    #[getter]
    pub fn status_code(&self) -> u16 {
        self.data.status.as_u16()
    }

    /// Set response status code
    #[setter]
    pub fn set_status_code(&mut self, status: u16) -> PyResult<()> {
        self.data.status = StatusCode::from_u16(status)
            .map_err(|e| PyRuntimeError::new_err(format!("Invalid status code: {}", e)))?;
        Ok(())
    }

    /// Get response headers
    #[getter]
    pub fn headers(&self) -> HashMap<String, String> {
        self.data.headers.clone()
    }

    /// Set header value
    pub fn set_header(&mut self, key: String, value: String) {
        self.data.set_header(key, value);
    }

    /// Get response body as bytes
    pub fn get_data(&self) -> &[u8] {
        &self.data.body
    }

    /// Get response body as string
    pub fn body_as_string(&self) -> PyResult<String> {
        self.data
            .body_as_string()
            .map_err(|e| PyRuntimeError::new_err(format!("Invalid UTF-8: {}", e)))
    }
}

impl PyResponse {
    pub fn from_response_data(data: ResponseData) -> Self {
        Self { data }
    }

    pub fn into_response_data(self) -> ResponseData {
        self.data
    }
}

/// Simple response cache for static responses
type ResponseCache = Arc<Mutex<HashMap<String, ResponseData>>>;

/// Fast Rust-only route handler for maximum performance testing
pub struct FastRouteHandler {
    response_body: String,
}

impl FastRouteHandler {
    pub fn new(response_body: String) -> Self {
        Self { response_body }
    }
}

#[async_trait]
impl RouteHandler for FastRouteHandler {
    async fn handle(&self, _req: RequestData) -> ResponseData {
        ResponseData::text(&self.response_body)
    }
}

/// Route handler for synchronous Python functions
pub struct PyRouteHandler {
    handler: PyObject,
    cache: ResponseCache,
}

impl PyRouteHandler {
    pub fn new(handler: PyObject) -> Self {
        Self {
            handler,
            cache: Arc::new(Mutex::new(HashMap::new())),
        }
    }
}

#[async_trait]
impl RouteHandler for PyRouteHandler {
    async fn handle(&self, req: RequestData) -> ResponseData {
        // Simplified approach: use tokio::task::spawn_blocking for Python calls
        let handler = self.handler.clone();

        let result = tokio::task::spawn_blocking(move || {
            Python::with_gil(|py| {
                let py_req = PyRequest::from_request_data(req);
                let py_req_obj = match Py::new(py, py_req) {
                    Ok(obj) => obj,
                    Err(e) => {
                        eprintln!("Failed to create PyRequest object: {:?}", e);
                        return ResponseData::error(
                            StatusCode::INTERNAL_SERVER_ERROR,
                            Some("Handler error"),
                        );
                    }
                };

                // Call the Python handler
                match handler.call1(py, (py_req_obj,)) {
                    Ok(result) => {
                        // Convert Python result to ResponseData
                        convert_python_result_to_response(py, result).unwrap_or_else(|e| {
                            eprintln!("Error converting Python response: {:?}", e);
                            ResponseData::error(
                                StatusCode::INTERNAL_SERVER_ERROR,
                                Some("Handler error"),
                            )
                        })
                    }
                    Err(e) => {
                        eprintln!("Error calling Python handler: {:?}", e);
                        ResponseData::error(StatusCode::INTERNAL_SERVER_ERROR, Some("Handler error"))
                    }
                }
            })
        })
        .await;

        match result {
            Ok(response_data) => response_data,
            Err(e) => {
                eprintln!("Error in spawn_blocking: {:?}", e);
                ResponseData::error(StatusCode::INTERNAL_SERVER_ERROR, Some("Handler error"))
            }
        }
    }
}

/// Route handler for asynchronous Python functions (simplified for now)
pub struct PyAsyncRouteHandler {
    handler: PyObject,
}

impl PyAsyncRouteHandler {
    pub fn new(handler: PyObject) -> Self {
        Self { handler }
    }
}

#[async_trait]
impl RouteHandler for PyAsyncRouteHandler {
    async fn handle(&self, req: RequestData) -> ResponseData {
        // Call the Python handler and detect if it returned a coroutine
        let call_result = Python::with_gil(|py| -> Result<(bool, PyObject), PyErr> {
            let py_req = PyRequest::from_request_data(req);
            let py_req_obj = Py::new(py, py_req)?;
            let out = self.handler.call1(py, (py_req_obj,))?;
            // Determine if this is a coroutine using asyncio.iscoroutine
            let asyncio = py.import("asyncio")?;
            let is_coro: bool = asyncio
                .call_method1("iscoroutine", (out.as_ref(py),))?
                .extract()?;
            Ok((is_coro, out))
        });

        let (is_coro, obj) = match call_result {
            Ok(v) => v,
            Err(e) => {
                eprintln!("Error calling async Python handler: {:?}", e);
                return ResponseData::error(
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Some("Async handler error"),
                );
            }
        };

        if is_coro {
            // Await the coroutine on the pyo3-asyncio integrated tokio runtime
            let fut = Python::with_gil(|py| pyo3_tokio::into_future(obj.as_ref(py)));
            let fut = match fut {
                Ok(f) => f,
                Err(e) => {
                    eprintln!("Error creating future from coroutine: {:?}", e);
                    return ResponseData::error(
                        StatusCode::INTERNAL_SERVER_ERROR,
                        Some("Async handler error"),
                    );
                }
            };

            match fut.await {
                Ok(py_result) => Python::with_gil(|py| {
                    convert_python_result_to_response(py, py_result).unwrap_or_else(|e| {
                        eprintln!("Error converting async Python response: {:?}", e);
                        ResponseData::error(
                            StatusCode::INTERNAL_SERVER_ERROR,
                            Some("Handler error"),
                        )
                    })
                }),
                Err(e) => {
                    eprintln!("Async Python handler raised: {:?}", e);
                    ResponseData::error(
                        StatusCode::INTERNAL_SERVER_ERROR,
                        Some("Async handler error"),
                    )
                }
            }
        } else {
            // Not a coroutine: convert directly to ResponseData
            Python::with_gil(|py| {
                convert_python_result_to_response(py, obj).unwrap_or_else(|e| {
                    eprintln!("Error converting Python response: {:?}", e);
                    ResponseData::error(StatusCode::INTERNAL_SERVER_ERROR, Some("Handler error"))
                })
            })
        }
    }
}

/// Helper function to convert serde_json::Value to Python object efficiently
fn json_value_to_python(py: Python, value: &serde_json::Value) -> PyResult<PyObject> {
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

/// Convert Python function result to ResponseData
fn convert_python_result_to_response(py: Python, result: PyObject) -> PyResult<ResponseData> {
    // Check if it's a tuple (body, status) or (body, status, headers)
    if let Ok(tuple) = result.downcast::<pyo3::types::PyTuple>(py) {
        match tuple.len() {
            2 => {
                let body = tuple.get_item(0)?;
                let status: u16 = tuple.get_item(1)?.extract()?;
                let mut response = create_response_from_python_object(py, body.into())?;
                response.status = StatusCode::from_u16(status)
                    .map_err(|e| PyRuntimeError::new_err(format!("Invalid status code: {}", e)))?;
                return Ok(response);
            }
            3 => {
                let body = tuple.get_item(0)?;
                let status: u16 = tuple.get_item(1)?.extract()?;
                let headers: HashMap<String, String> = tuple.get_item(2)?.extract()?;
                let mut response = create_response_from_python_object(py, body.into())?;
                response.status = StatusCode::from_u16(status)
                    .map_err(|e| PyRuntimeError::new_err(format!("Invalid status code: {}", e)))?;
                response.headers = headers;
                return Ok(response);
            }
            _ => {}
        }
    }

    // Default: treat as response body
    create_response_from_python_object(py, result)
}

/// Create ResponseData from Python object
fn create_response_from_python_object(py: Python, obj: PyObject) -> PyResult<ResponseData> {
    let mut response = ResponseData::new();

    if let Ok(bytes) = obj.downcast::<PyBytes>(py) {
        response.body = bytes.as_bytes().to_vec();
    } else if let Ok(string) = obj.downcast::<PyString>(py) {
        let text = string.to_string();
        response.body = text.into_bytes();
        response.set_header("Content-Type", "text/plain; charset=utf-8");
    } else {
        // Try to serialize as JSON
        let json_module = py.import("json")?;
        let json_str = json_module.call_method1("dumps", (obj,))?;
        let json_string: String = json_str.extract()?;
        response.body = json_string.into_bytes();
        response.set_header("Content-Type", "application/json");
    }

    Ok(response)
}
