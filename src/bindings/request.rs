//! Python wrapper for HTTP requests

use actix_web::HttpRequest;
use pyo3::prelude::*;
use std::collections::HashMap;

use crate::bindings::converters::*;

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
pub fn create_py_request(
    py: Python,
    req: &HttpRequest,
    body: &actix_web::web::Bytes,
) -> PyResult<Py<PyRequest>> {
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
