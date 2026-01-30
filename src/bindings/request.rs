//! Python wrapper for HTTP requests

use percent_encoding;
use pyo3::prelude::*;
use std::collections::HashMap;
use std::io::Write;

use crate::bindings::converters::*;

use pyo3::types::PyBytes;

/// Python wrapper for HTTP requests
#[pyclass]
pub struct PyRequest {
    pub(crate) inner: crate::request::RequestData,
}

/// Python wrapper for uploaded files
#[pyclass]
#[derive(Clone)]
pub struct PyUploadedFile {
    filename: String,
    content_type: String,
    content: Vec<u8>,
}

#[pymethods]
impl PyUploadedFile {
    #[getter]
    pub fn filename(&self) -> &str {
        &self.filename
    }

    #[getter]
    pub fn content_type(&self) -> &str {
        &self.content_type
    }

    pub fn save(&self, path: String) -> PyResult<()> {
        let mut file = std::fs::File::create(path)?;
        file.write_all(&self.content)?;
        Ok(())
    }
}

#[pymethods]
impl PyRequest {
    #[getter]
    pub fn method(&self) -> &str {
        self.inner.method_str()
    }

    #[getter]
    pub fn path(&self) -> &str {
        &self.inner.path
    }

    #[getter]
    pub fn query_string(&self) -> &str {
        &self.inner.query_string
    }

    #[getter]
    pub fn headers(&self) -> HashMap<String, String> {
        self.inner.headers.clone()
    }

    #[getter]
    pub fn args(&self) -> HashMap<String, String> {
        self.inner.query_params.clone()
    }

    #[getter]
    pub fn files(&self, py: Python) -> HashMap<String, Py<PyUploadedFile>> {
        let mut py_files = HashMap::new();
        for (key, file) in &self.inner.files {
            if let Ok(py_file) = Py::new(
                py,
                PyUploadedFile {
                    filename: file.filename.clone(),
                    content_type: file.content_type.clone(),
                    content: file.content.clone(),
                },
            ) {
                py_files.insert(key.clone(), py_file);
            }
        }
        py_files
    }

    pub fn get_data(&self, py: Python) -> Py<PyBytes> {
        PyBytes::new(py, &self.inner.body).into()
    }

    pub fn json(&self, py: Python) -> PyResult<Py<PyAny>> {
        if self.inner.body.is_empty() {
            return Ok(py.None());
        }

        // Try direct serde_json conversion first (fast path)
        match serde_json::from_slice::<serde_json::Value>(&self.inner.body) {
            Ok(value) => json_value_to_python(py, &value),
            Err(_) => {
                // Fallback to Python's json.loads for compliance/error handling
                let json_str = String::from_utf8_lossy(&self.inner.body);
                let json_module = py.import("json")?;
                let result = json_module.call_method1("loads", (json_str.to_string(),))?;
                Ok(result.into())
            }
        }
    }

    pub fn is_json(&self) -> bool {
        self.inner.is_json()
    }

    pub fn form(&self, _py: Python) -> HashMap<String, String> {
        if self.inner.is_form() {
            self.inner.parse_form_data()
        } else if !self.inner.multipart_form.is_empty() {
            self.inner.multipart_form.clone()
        } else {
            HashMap::new()
        }
    }

    #[getter]
    pub fn cookies(&self) -> HashMap<String, String> {
        self.inner.get_cookies()
    }
}

/// Create PyRequest from generic RequestData by taking ownership
pub fn create_py_request(py: Python, req: crate::request::RequestData) -> PyResult<Py<PyRequest>> {
    let py_req = PyRequest { inner: req };

    Py::new(py, py_req)
}
