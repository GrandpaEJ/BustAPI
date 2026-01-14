//! Typed Turbo Route Handler
//!
//! Ultra-fast handler for routes with typed path parameters.
//! Parameters are parsed and converted in Rust before calling Python.
//! Optional response caching for maximum performance.

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyFloat, PyInt, PyString};
use std::collections::HashMap;
use std::sync::RwLock;
use std::time::{Duration, Instant};

use crate::bindings::converters::convert_py_result_to_response;
use crate::request::RequestData;
use crate::response::ResponseData;
use crate::router::RouteHandler;

/// Cached response with expiration time
#[derive(Clone)]
struct CachedResponse {
    response: ResponseData,
    expires_at: Instant,
}

impl CachedResponse {
    fn new(response: ResponseData, ttl_secs: u64) -> Self {
        Self {
            response,
            expires_at: Instant::now() + Duration::from_secs(ttl_secs),
        }
    }

    fn is_expired(&self) -> bool {
        Instant::now() > self.expires_at
    }
}

/// Parameter type specification
#[derive(Debug, Clone)]
pub enum ParamType {
    Int,
    Float,
    Str,
    Path, // Wildcard path segment
}

impl ParamType {
    pub fn from_str(s: &str) -> Self {
        match s.to_lowercase().as_str() {
            "int" => ParamType::Int,
            "float" => ParamType::Float,
            "path" => ParamType::Path,
            _ => ParamType::Str,
        }
    }
}

/// Parsed parameter value
#[derive(Debug, Clone)]
pub enum TypedValue {
    Int(i64),
    BigInt(String), // For overflow, let Python handle
    Float(f64),
    Str(String),
}

/// Typed turbo route handler with optional caching
pub struct PyTypedTurboHandler {
    handler: Py<PyAny>,
    pattern: String,
    /// (param_name, param_type) in order of appearance in route
    param_specs: Vec<(String, ParamType)>,
    /// Cache TTL in seconds (0 = no caching)
    cache_ttl: u64,
    /// Response cache: path -> cached response
    cache: RwLock<HashMap<String, CachedResponse>>,
}

impl PyTypedTurboHandler {
    #[allow(dead_code)]
    pub fn new(handler: Py<PyAny>, pattern: String, param_types: HashMap<String, String>) -> Self {
        Self::with_cache(handler, pattern, param_types, 0)
    }

    pub fn with_cache(
        handler: Py<PyAny>,
        pattern: String,
        param_types: HashMap<String, String>,
        cache_ttl: u64,
    ) -> Self {
        // Parse pattern to get param order
        let param_specs = Self::parse_pattern(&pattern, &param_types);

        Self {
            handler,
            pattern,
            param_specs,
            cache_ttl,
            cache: RwLock::new(HashMap::new()),
        }
    }

    /// Parse route pattern and build ordered param specs
    fn parse_pattern(
        pattern: &str,
        param_types: &HashMap<String, String>,
    ) -> Vec<(String, ParamType)> {
        let mut specs = Vec::new();

        for part in pattern.split('/') {
            if part.starts_with('<') && part.ends_with('>') {
                let inner = &part[1..part.len() - 1];
                let name = if let Some((_, n)) = inner.split_once(':') {
                    n.trim().to_string()
                } else {
                    inner.trim().to_string()
                };

                let param_type = param_types
                    .get(&name)
                    .map(|t| ParamType::from_str(t))
                    .unwrap_or(ParamType::Str);

                specs.push((name, param_type));
            }
        }

        specs
    }

    /// Extract and convert parameters from request path
    fn extract_params(&self, path: &str) -> Result<HashMap<String, TypedValue>, String> {
        let pattern_parts: Vec<&str> = self.pattern.trim_matches('/').split('/').collect();
        let path_parts: Vec<&str> = path.trim_matches('/').split('/').collect();

        let mut params = HashMap::new();
        let mut spec_idx = 0;

        for (i, pp) in pattern_parts.iter().enumerate() {
            if pp.starts_with('<') && pp.ends_with('>') {
                if spec_idx >= self.param_specs.len() {
                    return Err("Parameter spec mismatch".to_string());
                }

                let (name, param_type) = &self.param_specs[spec_idx];
                spec_idx += 1;

                // Handle path wildcard (matches rest of path)
                if matches!(param_type, ParamType::Path) {
                    let remaining: String = path_parts[i..].join("/");
                    params.insert(name.clone(), TypedValue::Str(remaining));
                    break;
                }

                if i >= path_parts.len() {
                    return Err(format!("Missing path segment for parameter '{}'", name));
                }

                let value = path_parts[i];
                let typed_value = match param_type {
                    ParamType::Int => {
                        // Try fast i64 parse first
                        match value.parse::<i64>() {
                            Ok(n) => TypedValue::Int(n),
                            Err(_) => {
                                // Check if it's a valid big integer (let Python handle)
                                if value.chars().all(|c| c.is_ascii_digit() || c == '-') {
                                    TypedValue::BigInt(value.to_string())
                                } else {
                                    return Err(format!(
                                        "Parameter '{}': expected int, got '{}'",
                                        name, value
                                    ));
                                }
                            }
                        }
                    }
                    ParamType::Float => match value.parse::<f64>() {
                        Ok(n) => TypedValue::Float(n),
                        Err(_) => {
                            return Err(format!(
                                "Parameter '{}': expected float, got '{}'",
                                name, value
                            ))
                        }
                    },
                    ParamType::Str | ParamType::Path => TypedValue::Str(value.to_string()),
                };

                params.insert(name.clone(), typed_value);
            }
        }

        Ok(params)
    }

    /// Convert params to Python dict with proper types
    fn to_py_dict(&self, py: Python, params: &HashMap<String, TypedValue>) -> PyResult<Py<PyDict>> {
        let dict = PyDict::new(py);

        for (name, value) in params {
            match value {
                TypedValue::Int(n) => {
                    dict.set_item(name, PyInt::new(py, *n))?;
                }
                TypedValue::BigInt(s) => {
                    // Use Python's int() for arbitrary precision
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

impl RouteHandler for PyTypedTurboHandler {
    fn handle(&self, req: RequestData) -> ResponseData {
        let cache_key = req.path.clone();

        // Check cache first (if caching is enabled)
        if self.cache_ttl > 0 {
            if let Ok(cache) = self.cache.read() {
                if let Some(cached) = cache.get(&cache_key) {
                    if !cached.is_expired() {
                        return cached.response.clone();
                    }
                }
            }
        }

        // Extract params from path
        let params = match self.extract_params(&req.path) {
            Ok(p) => p,
            Err(e) => {
                return ResponseData::json_error(actix_web::http::StatusCode::BAD_REQUEST, &e);
            }
        };

        let response = Python::attach(|py| {
            // Convert to Python dict
            let py_params = match self.to_py_dict(py, &params) {
                Ok(d) => d,
                Err(e) => {
                    tracing::error!("Failed to convert params to Python: {:?}", e);
                    return ResponseData::error(
                        actix_web::http::StatusCode::INTERNAL_SERVER_ERROR,
                        Some("Parameter conversion error"),
                    );
                }
            };

            // Call Python handler with (rust_request=None, path_params=dict)
            // We pass None for rust_request since typed turbo doesn't use it
            match self.handler.call1(py, (py.None(), py_params)) {
                Ok(result) => convert_py_result_to_response(py, result, &req.headers),
                Err(e) => {
                    tracing::error!("Typed turbo handler error: {:?}", e);
                    ResponseData::error(
                        actix_web::http::StatusCode::INTERNAL_SERVER_ERROR,
                        Some("Handler error"),
                    )
                }
            }
        });

        // Store in cache (if caching is enabled and response is successful)
        if self.cache_ttl > 0 && response.status.is_success() {
            if let Ok(mut cache) = self.cache.write() {
                cache.insert(
                    cache_key,
                    CachedResponse::new(response.clone(), self.cache_ttl),
                );
            }
        }

        response
    }
}
