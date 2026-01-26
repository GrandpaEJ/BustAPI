//! Python route handlers

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyFloat, PyInt, PyString};
use std::collections::HashMap;

use crate::bindings::converters::*;
use crate::bindings::request::create_py_request;
use crate::request::RequestData;
use crate::response::ResponseData;
use crate::router::RouteHandler;

// Reuse ParamType and TypedValue from typed_turbo
pub use crate::bindings::typed_turbo::{ParamType, TypedValue};

/// Python route handler - calls Python function for each request
/// Now with Rust-side path parameter extraction for performance!
pub struct PyRouteHandler {
    handler: Py<PyAny>,
    pattern: String,
    /// Pre-parsed param specs: (name, type) in order
    param_specs: Vec<(String, ParamType)>,
}

impl PyRouteHandler {
    /// Create handler with pattern for path param extraction
    pub fn with_pattern(
        handler: Py<PyAny>,
        pattern: String,
        param_types: HashMap<String, String>,
    ) -> Self {
        let param_specs = Self::parse_pattern(&pattern, &param_types);
        Self {
            handler,
            pattern,
            param_specs,
        }
    }

    /// Legacy constructor (no path params)
    pub fn new(handler: Py<PyAny>) -> Self {
        Self {
            handler,
            pattern: String::new(),
            param_specs: Vec::new(),
        }
    }

    /// Parse route pattern to extract param specs
    fn parse_pattern(
        pattern: &str,
        param_types: &HashMap<String, String>,
    ) -> Vec<(String, ParamType)> {
        let mut specs = Vec::new();

        for part in pattern.split('/') {
            if part.starts_with('<') && part.ends_with('>') {
                let inner = &part[1..part.len() - 1];
                let (type_hint, name) = if let Some((t, n)) = inner.split_once(':') {
                    (t.trim(), n.trim())
                } else {
                    ("str", inner.trim())
                };

                // Use explicit type from registration, or infer from pattern
                let param_type = param_types
                    .get(name)
                    .map(|t| ParamType::from_str(t))
                    .unwrap_or_else(|| ParamType::from_str(type_hint));

                specs.push((name.to_string(), param_type));
            }
        }

        specs
    }

    /// Extract typed params from request path
    fn extract_params(&self, path: &str) -> Option<HashMap<String, TypedValue>> {
        if self.param_specs.is_empty() {
            return None;
        }

        let pattern_parts: Vec<&str> = self.pattern.trim_matches('/').split('/').collect();
        let path_parts: Vec<&str> = path.trim_matches('/').split('/').collect();

        if pattern_parts.len() != path_parts.len() {
            return None;
        }

        let mut params = HashMap::new();
        let mut spec_idx = 0;

        for (i, pp) in pattern_parts.iter().enumerate() {
            if pp.starts_with('<') && pp.ends_with('>') {
                if spec_idx >= self.param_specs.len() || i >= path_parts.len() {
                    return None;
                }

                let (name, param_type) = &self.param_specs[spec_idx];
                spec_idx += 1;

                let value = path_parts[i];
                let typed_value = match param_type {
                    ParamType::Int => {
                        match value.parse::<i64>() {
                            Ok(n) => TypedValue::Int(n),
                            Err(_) => {
                                if value.chars().all(|c| c.is_ascii_digit() || c == '-') {
                                    TypedValue::BigInt(value.to_string())
                                } else {
                                    return None; // Invalid int
                                }
                            }
                        }
                    }
                    ParamType::Float => match value.parse::<f64>() {
                        Ok(n) => TypedValue::Float(n),
                        Err(_) => return None,
                    },
                    ParamType::Str | ParamType::Path => TypedValue::Str(value.to_string()),
                };

                params.insert(name.clone(), typed_value);
            }
        }

        Some(params)
    }

    /// Convert params to Python dict
    fn to_py_dict(&self, py: Python, params: &HashMap<String, TypedValue>) -> PyResult<Py<PyDict>> {
        let dict = PyDict::new(py);

        for (name, value) in params {
            match value {
                TypedValue::Int(n) => {
                    dict.set_item(name, PyInt::new(py, *n))?;
                }
                TypedValue::BigInt(s) => {
                    let int_type = py.get_type::<PyInt>();
                    let py_int = int_type.call1((s,))?;
                    dict.set_item(name, py_int)?;
                }
                TypedValue::Float(n) => {
                    dict.set_item(name, PyFloat::new(py, *n))?;
                }
                TypedValue::Str(s) => {
                    dict.set_item(name, PyString::new(py, s))?;
                }
            }
        }

        Ok(dict.into())
    }
}

impl RouteHandler for PyRouteHandler {
    fn handle(&self, req: RequestData) -> ResponseData {
        Python::attach(|py| {
            // Create request object
            let py_req = create_py_request(py, &req);

            match py_req {
                Ok(py_req_obj) => {
                    // Extract path params in Rust (fast path)
                    let py_params = if !self.param_specs.is_empty() {
                        match self.extract_params(&req.path) {
                            Some(params) => self.to_py_dict(py, &params).ok(),
                            None => None,
                        }
                    } else {
                        None
                    };

                    // Call Python handler with (rust_request, path_params)
                    let call_result = match py_params {
                        Some(params) => self.handler.call1(py, (py_req_obj, params)),
                        None => self.handler.call1(py, (py_req_obj, py.None())),
                    };

                    match call_result {
                        Ok(result) => convert_py_result_to_response(py, result, &req.headers),
                        Err(e) => {
                            tracing::error!("Python handler error: {:?}", e);
                            ResponseData::error(
                                actix_web::http::StatusCode::INTERNAL_SERVER_ERROR,
                                Some("Handler error"),
                            )
                        }
                    }
                }
                Err(e) => {
                    tracing::error!("Request creation error: {:?}", e);
                    ResponseData::error(
                        actix_web::http::StatusCode::INTERNAL_SERVER_ERROR,
                        Some("Request error"),
                    )
                }
            }
        })
    }
}

/// Async Python route handler
pub struct PyAsyncRouteHandler {
    handler: Py<PyAny>,
}

impl PyAsyncRouteHandler {
    pub fn new(handler: Py<PyAny>) -> Self {
        Self { handler }
    }
}

impl RouteHandler for PyAsyncRouteHandler {
    fn handle(&self, req: RequestData) -> ResponseData {
        // For async handlers, call and check if coroutine
        Python::attach(|py| {
            let py_req = create_py_request(py, &req);

            match py_req {
                Ok(py_req_obj) => {
                    match self.handler.call1(py, (py_req_obj,)) {
                        Ok(result) => {
                            // Check if coroutine
                            let asyncio = py.import("asyncio");
                            if let Ok(asyncio) = asyncio {
                                match asyncio.call_method1("iscoroutine", (&result,)) {
                                    Ok(is_coro) => {
                                        let is_coro_bool =
                                            is_coro.extract::<bool>().unwrap_or(false);
                                        tracing::debug!(
                                            "Async handler result type: {}, is_coro: {}",
                                            result
                                                .bind(py)
                                                .get_type()
                                                .name()
                                                .ok()
                                                .map(|s| s.to_string())
                                                .unwrap_or("unknown".to_string()),
                                            is_coro_bool
                                        );

                                        if is_coro_bool {
                                            // Run coroutine
                                            if let Ok(_loop_obj) =
                                                asyncio.call_method0("NewEventLoop")
                                            { // Try new loop? No get_event_loop
                                                 // ...
                                            }
                                            // Revert to old logic but with logging
                                            if let Ok(loop_obj) =
                                                asyncio.call_method0("get_event_loop")
                                            {
                                                if let Ok(awaited) = loop_obj
                                                    .call_method1("run_until_complete", (&result,))
                                                {
                                                    return convert_py_result_to_response(
                                                        py,
                                                        awaited.into(),
                                                        &req.headers,
                                                    );
                                                } else {
                                                    tracing::error!("run_until_complete failed");
                                                }
                                            } else {
                                                // Try new loop if get_event_loop fails (e.g. no loop in thread)
                                                if let Ok(loop_obj) =
                                                    asyncio.call_method0("new_event_loop")
                                                {
                                                    let _ = asyncio.call_method1(
                                                        "set_event_loop",
                                                        (&loop_obj,),
                                                    );
                                                    if let Ok(awaited) = loop_obj.call_method1(
                                                        "run_until_complete",
                                                        (&result,),
                                                    ) {
                                                        return convert_py_result_to_response(
                                                            py,
                                                            awaited.into(),
                                                            &req.headers,
                                                        );
                                                    }
                                                }
                                                tracing::error!("Failed to get/create event loop");
                                            }
                                        }
                                    }
                                    Err(e) => tracing::error!("iscoroutine check failed: {:?}", e),
                                }
                            }
                            convert_py_result_to_response(py, result, &req.headers)
                        }
                        Err(e) => {
                            tracing::error!("Async handler error: {:?}", e);
                            ResponseData::error(
                                actix_web::http::StatusCode::INTERNAL_SERVER_ERROR,
                                Some("Async handler error"),
                            )
                        }
                    }
                }
                Err(e) => {
                    tracing::error!("Request creation error: {:?}", e);
                    ResponseData::error(
                        actix_web::http::StatusCode::INTERNAL_SERVER_ERROR,
                        Some("Request error"),
                    )
                }
            }
        })
    }
}
