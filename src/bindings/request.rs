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
    method: String,
    path: String,
    query_string: String,
    headers: HashMap<String, String>,
    args: HashMap<String, String>,
    body: Py<PyBytes>,
    files: HashMap<String, Py<PyUploadedFile>>,
    multipart_form: HashMap<String, String>,
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

    #[getter]
    pub fn files(&self, py: Python) -> HashMap<String, Py<PyUploadedFile>> {
        self.files
            .iter()
            .map(|(k, v)| (k.clone(), v.clone_ref(py)))
            .collect()
    }

    pub fn get_data(&self, py: Python) -> Py<PyBytes> {
        self.body.clone_ref(py)
    }

    pub fn json(&self, py: Python) -> PyResult<Py<PyAny>> {
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
        } else if !self.multipart_form.is_empty() {
            self.multipart_form.clone()
        } else {
            HashMap::new()
        }
    }

    #[getter]
    pub fn cookies(&self) -> HashMap<String, String> {
        let mut cookies = HashMap::new();

        if let Some(cookie_header) = self
            .headers
            .iter()
            .find(|(k, _)| k.to_lowercase() == "cookie")
            .map(|(_, v)| v)
        {
            for cookie_pair in cookie_header.split(';') {
                let cookie_pair = cookie_pair.trim();
                if let Some((key, value)) = cookie_pair.split_once('=') {
                    // URL decode cookie values using percent_encoding
                    let decoded_value = percent_encoding::percent_decode_str(value.trim())
                        .decode_utf8()
                        .unwrap_or_else(|_| std::borrow::Cow::Borrowed(value.trim()));
                    cookies.insert(key.trim().to_string(), decoded_value.to_string());
                }
            }
        }

        cookies
    }
}

/// Create PyRequest from generic RequestData
pub fn create_py_request(py: Python, req: &crate::request::RequestData) -> PyResult<Py<PyRequest>> {
    let py_body = PyBytes::new(py, &req.body);

    let mut py_files = HashMap::new();
    for (key, file) in &req.files {
        let py_file = Py::new(
            py,
            PyUploadedFile {
                filename: file.filename.clone(),
                content_type: file.content_type.clone(),
                content: file.content.clone(),
            },
        )?;
        py_files.insert(key.clone(), py_file);
    }

    let py_req = PyRequest {
        method: req.method.as_str().to_string(),
        path: req.path.clone(),
        query_string: req.query_string.clone(),
        headers: req.headers.clone(),
        args: req.query_params.clone(),
        body: py_body.into(),
        files: py_files,
        multipart_form: req.multipart_form.clone(),
    };

    Py::new(py, py_req)
}
