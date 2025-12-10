//! Python wrapper for HTTP requests

use pyo3::prelude::*;
use std::collections::HashMap;

use crate::bindings::converters::*;

use pyo3::types::PyBytes;

/// Python wrapper for HTTP requests
#[pyclass]
pub struct PyRequest {
    method: String,
    path: String,
    query_string: String,
    headers: HashMap<String, String>,
    args: HashMap<String, String>,
    body: Py<PyBytes>,
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

    #[getter]
    pub fn args(&self) -> HashMap<String, String> {
        self.args.clone()
    }

    pub fn get_data(&self, py: Python) -> Py<PyBytes> {
        self.body.clone_ref(py)
    }

    pub fn json(&self, py: Python) -> PyResult<PyObject> {
        let body_bytes = self.body.as_bytes(py);
        let json_str = String::from_utf8_lossy(body_bytes);
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

    pub fn is_json(&self) -> bool {
        self.headers.iter().any(|(k, v)| {
            k.to_lowercase() == "content-type" && v.to_lowercase().contains("application/json")
        })
    }

    pub fn form(&self, py: Python) -> HashMap<String, String> {
        let content_type = self
            .headers
            .iter()
            .find(|(k, _)| k.to_lowercase() == "content-type")
            .map(|(_, v)| v.to_lowercase())
            .unwrap_or_default();

        if content_type.contains("application/x-www-form-urlencoded") {
            let body_bytes = self.body.as_bytes(py);
            String::from_utf8(body_bytes.to_vec())
                .ok()
                .map(|s| {
                    url::form_urlencoded::parse(s.as_bytes())
                        .into_owned()
                        .collect()
                })
                .unwrap_or_default()
        } else {
            HashMap::new()
        }
    }
}

/// Create PyRequest from generic RequestData
pub fn create_py_request(py: Python, req: &crate::request::RequestData) -> PyResult<Py<PyRequest>> {
    let py_body = PyBytes::new(py, &req.body);
    
    let py_req = PyRequest {
        method: req.method.as_str().to_string(),
        path: req.path.clone(),
        query_string: req.query_string.clone(),
        headers: req.headers.clone(),
        args: req.query_params.clone(),
        body: py_body.into(),
    };

    Py::new(py, py_req)
}
