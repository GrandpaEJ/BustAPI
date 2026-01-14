//! Conversion utilities between Python and Rust types

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyString, PyTuple};
use std::collections::HashMap;

/// Convert Python result to ResponseData
pub fn convert_py_result_to_response(
    py: Python,
    result: Py<PyAny>,
    req_headers: &HashMap<String, String>,
) -> crate::response::ResponseData {
    use crate::response::ResponseData;
    use http::StatusCode;
    use std::path::Path;

    // FIRST: Check for explicit path attribute (FileResponse optimization)
    // This must come before generic Response check since FileResponse inherits from Response
    if let Ok(path_obj) = result.getattr(py, "path") {
        if let Ok(path_str) = path_obj.extract::<String>(py) {
            // It's a file response! Use Actix's NamedFile via ResponseData (handled in server/handlers.rs)
            let path = Path::new(&path_str);
            if path.exists() {
                let mut resp = ResponseData::new();
                resp.file_path = Some(path_str);

                // Copy Status
                if let Ok(status_code) = result.getattr(py, "status_code") {
                    if let Ok(status) = status_code.extract::<u16>(py) {
                        resp.set_status(StatusCode::from_u16(status).unwrap_or(StatusCode::OK));
                    }
                }

                // Copy Headers
                if let Ok(headers) = result.getattr(py, "headers") {
                    if let Ok(header_dict) = headers.extract::<HashMap<String, String>>(py) {
                        for (k, v) in header_dict {
                            // Don't overwrite Content-Length from file serving
                            if k.to_lowercase() != "content-length" {
                                resp.set_header(&k, &v);
                            }
                        }
                    } else if let Ok(items) = headers.call_method0(py, "items") {
                        // Handle wsgiref.headers or other mapping types
                        if let Ok(iter) = items.bind(py).try_iter() {
                            for item in iter.flatten() {
                                if let Ok((k, v)) = item.extract::<(String, String)>() {
                                    if k.to_lowercase() != "content-length" {
                                        resp.set_header(&k, &v);
                                    }
                                }
                            }
                        }
                    }
                }
                return resp;
            }
        }
    }

    // STREAMING: Check for content attribute (for StreamingResponse)
    if let Ok(content_obj) = result.getattr(py, "content") {
        // Verify it isn't None (Response base sometimes has content property?)
        if !content_obj.is_none(py) {
            let mut resp = ResponseData::new();
            resp.stream_iterator = Some(content_obj);

            // Copy Status
            if let Ok(status_code) = result.getattr(py, "status_code") {
                if let Ok(status) = status_code.extract::<u16>(py) {
                    resp.set_status(StatusCode::from_u16(status).unwrap_or(StatusCode::OK));
                }
            }

            // Copy Headers
            if let Ok(headers) = result.getattr(py, "headers") {
                if let Ok(header_dict) = headers.extract::<HashMap<String, String>>(py) {
                    for (k, v) in header_dict {
                        if k.to_lowercase() != "content-length" {
                            resp.set_header(&k, &v);
                        }
                    }
                } else if let Ok(items) = headers.call_method0(py, "items") {
                    if let Ok(iter) = items.bind(py).try_iter() {
                        for item in iter.flatten() {
                            if let Ok((k, v)) = item.extract::<(String, String)>() {
                                if k.to_lowercase() != "content-length" {
                                    resp.set_header(&k, &v);
                                }
                            }
                        }
                    }
                }
            }

            // Ensure Content-Type is set if missing (headers might not reflect self.content_type if not synced)
            if let Ok(ct_prop) = result.getattr(py, "content_type") {
                if let Ok(ct) = ct_prop.extract::<String>(py) {
                    if !resp.headers.contains_key("Content-Type")
                        && !resp.headers.contains_key("content-type")
                    {
                        resp.set_header("Content-Type", &ct);
                    }
                }
            }

            return resp;
        }
    }

    // Check if tuple (body, status) or (body, status, headers)
    if let Ok(tuple) = result.cast_bound::<PyTuple>(py) {
        match tuple.len() {
            2 => {
                if let (Ok(body), Ok(status)) = (
                    tuple.get_item(0),
                    tuple.get_item(1).and_then(|s| s.extract::<u16>()),
                ) {
                    let response_body = python_to_response_body(py, body.into());
                    let mut resp = ResponseData::with_body(response_body.into_bytes());
                    resp.set_status(StatusCode::from_u16(status).unwrap_or(StatusCode::OK));
                    resp.set_header("Content-Type", "application/json");
                    return resp;
                }
            }
            3 => {
                if let (Ok(body), Ok(status), Ok(hdrs)) = (
                    tuple.get_item(0),
                    tuple.get_item(1).and_then(|s| s.extract::<u16>()),
                    tuple
                        .get_item(2)
                        .and_then(|h| h.extract::<HashMap<String, String>>()),
                ) {
                    let response_body = python_to_response_body(py, body.into());
                    let status_code = StatusCode::from_u16(status).unwrap_or(StatusCode::OK);

                    let mut resp = ResponseData::with_status(status_code);
                    let mut content_type = "application/json".to_string();

                    // Set headers
                    for (k, v) in &hdrs {
                        if k.to_lowercase() == "content-type" {
                            content_type = v.clone();
                        }
                        resp.set_header(k, v);
                    }

                    resp.set_header("Content-Type", content_type);
                    resp.set_body(response_body.into_bytes());
                    return resp;
                }
            }
            _ => {}
        }
    }

    // Check for explicit path attribute (FileResponse optimization)
    tracing::debug!("Checking for path attribute on result object");
    if let Ok(path_obj) = result.getattr(py, "path") {
        tracing::debug!("Found path attribute!");
        if let Ok(path_str) = path_obj.extract::<String>(py) {
            tracing::debug!("Extracted path string: {}", path_str);
            // It's a file response! Use Rust's file serving logic with Range support
            let path = Path::new(&path_str);
            if path.exists() {
                // Debug headers
                tracing::debug!(
                    "Path exists. Incoming headers: {:?}",
                    req_headers.keys().collect::<Vec<_>>()
                );

                let mut resp = ResponseData::new();
                resp.file_path = Some(path_str);

                // Copy Status
                if let Ok(status_code) = result.getattr(py, "status_code") {
                    if let Ok(status) = status_code.extract::<u16>(py) {
                        resp.set_status(StatusCode::from_u16(status).unwrap_or(StatusCode::OK));
                    }
                }

                // Copy Headers
                if let Ok(headers) = result.getattr(py, "headers") {
                    if let Ok(header_dict) = headers.extract::<HashMap<String, String>>(py) {
                        for (k, v) in header_dict {
                            // Don't overwrite Content-Length from file serving
                            if k.to_lowercase() != "content-length" {
                                resp.set_header(&k, &v);
                            }
                        }
                    } else if let Ok(items) = headers.call_method0(py, "items") {
                        // Handle wsgiref.headers or other mapping types
                        if let Ok(iter) = items.bind(py).try_iter() {
                            for item in iter.flatten() {
                                if let Ok((k, v)) = item.extract::<(String, String)>() {
                                    if k.to_lowercase() != "content-length" {
                                        resp.set_header(&k, &v);
                                    }
                                }
                            }
                        }
                    }
                }
                return resp;
            }
        }
    }

    // Check for Response object (duck typing)
    // Look for .status_code, .headers, .get_data()
    if let Ok(status_code) = result.getattr(py, "status_code") {
        if let Ok(headers) = result.getattr(py, "headers") {
            if let Ok(get_data) = result.getattr(py, "get_data") {
                // It looks like a Response object!

                // Extract status
                let status = status_code.extract::<u16>(py).unwrap_or(200);

                // Extract body
                let body_obj = get_data.call0(py).unwrap_or_else(|_| result.clone_ref(py));
                let body_bytes = if let Ok(bytes) = body_obj.extract::<Vec<u8>>(py) {
                    bytes
                } else if let Ok(s) = body_obj.extract::<String>(py) {
                    s.into_bytes()
                } else {
                    Vec::new()
                };

                let mut resp = ResponseData::with_body(body_bytes);
                resp.set_status(StatusCode::from_u16(status).unwrap_or(StatusCode::OK));

                // Extract headers
                // headers might be a dict or Headers object. try converting to dict
                if let Ok(header_dict) = headers.extract::<HashMap<String, String>>(py) {
                    for (k, v) in header_dict {
                        resp.set_header(&k, &v);
                    }
                } else {
                    // Try iterating if it's not a dict, e.g. wsgiref.headers.Headers
                    if let Ok(items) = headers.call_method0(py, "items") {
                        if let Ok(iter) = items.bind(py).try_iter() {
                            for item in iter.flatten() {
                                // Extract tuple (key, value)
                                if let Ok((k, v)) = item.extract::<(String, String)>() {
                                    resp.set_header(&k, &v);
                                }
                            }
                        }
                    }
                }

                return resp;
            }
        }
    }

    // Default: treat as response body
    let body = python_to_response_body(py, result);
    let trimmed = body.trim();

    if trimmed.starts_with("<") {
        ResponseData::html(body)
    } else if trimmed.starts_with("{") || trimmed.starts_with("[") {
        let mut resp = ResponseData::with_body(body.into_bytes());
        resp.set_header("Content-Type", "application/json");
        resp
    } else {
        // Default to text/plain for other strings
        ResponseData::text(body)
    }
}

use serde::ser::{Serialize, SerializeMap, SerializeSeq, Serializer};

/// Convert Python object to response body bytes
pub fn python_to_response_body(py: Python, obj: Py<PyAny>) -> String {
    if let Ok(bytes) = obj.cast_bound::<PyBytes>(py) {
        return String::from_utf8_lossy(bytes.as_bytes()).to_string();
    }

    if let Ok(string) = obj.cast_bound::<PyString>(py) {
        return string.to_string();
    }

    // Optimization: Zero-Allocation Serialization
    // We implement serde::Serialize for a wrapper type that holds the PyObject
    // This allows serde_json to write directly to the string buffer without
    // creating an intermediate serde_json::Value DOM.
    let obj_ref = obj.bind(py);
    if obj_ref.is_instance_of::<PyDict>()
        || obj_ref.is_instance_of::<pyo3::types::PyList>()
        || obj_ref.is_instance_of::<pyo3::types::PyTuple>()
    {
        let serializer = PyJson(obj_ref);
        match serde_json::to_string(&serializer) {
            Ok(s) => return s,
            Err(e) => tracing::warn!("Native zero-copy serialization failed: {:?}", e),
        }
    }

    // Try JSON serialization (Fallback)
    if let Ok(json_module) = py.import("json") {
        if let Ok(json_str) = json_module.call_method1("dumps", (&obj,)) {
            if let Ok(s) = json_str.extract::<String>() {
                return s;
            }
        }
    }

    "{}".to_string()
}

// Wrapper struct for Zero-Copy Serialization
struct PyJson<'a>(&'a Bound<'a, PyAny>);

impl<'a> Serialize for PyJson<'a> {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        use pyo3::types::*;
        let obj = self.0;

        if obj.is_none() {
            return serializer.serialize_none();
        }

        if let Ok(s) = obj.cast::<PyString>() {
            return serializer.serialize_str(s.to_string_lossy().as_ref());
        }

        if let Ok(b) = obj.cast::<PyBool>() {
            return serializer.serialize_bool(b.is_true());
        }

        if let Ok(i) = obj.cast::<PyInt>() {
            if let Ok(val) = i.extract::<i64>() {
                return serializer.serialize_i64(val);
            }
            // Fallback for huge integers if needed, but for now i64 is reasonable
            return serializer.serialize_str(&i.to_string());
        }

        if let Ok(f) = obj.cast::<PyFloat>() {
            if let Ok(val) = f.extract::<f64>() {
                return serializer.serialize_f64(val);
            }
        }

        if let Ok(l) = obj.cast::<PyList>() {
            let mut seq = serializer.serialize_seq(Some(l.len()))?;
            for item in l {
                seq.serialize_element(&PyJson(&item))?;
            }
            return seq.end();
        }

        if let Ok(t) = obj.cast::<PyTuple>() {
            let mut seq = serializer.serialize_seq(Some(t.len()))?;
            for item in t {
                seq.serialize_element(&PyJson(&item))?;
            }
            return seq.end();
        }

        if let Ok(d) = obj.cast::<PyDict>() {
            let mut map = serializer.serialize_map(Some(d.len()))?;
            for (k, v) in d {
                let key_str = k.extract::<String>().map_err(serde::ser::Error::custom)?;
                map.serialize_entry(&key_str, &PyJson(&v))?;
            }
            return map.end();
        }

        // Fallback for unknown types -> String
        serializer.serialize_str(&obj.to_string())
    }
}

/// Convert serde_json::Value to Python object
#[allow(deprecated)]
pub fn json_value_to_python(py: Python, value: &serde_json::Value) -> PyResult<Py<PyAny>> {
    use pyo3::types::PyBool;

    match value {
        serde_json::Value::Null => Ok(py.None()),
        serde_json::Value::Bool(b) => Ok(PyBool::new(py, *b).to_owned().into_any().unbind()),
        serde_json::Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(pyo3::types::PyInt::new(py, i).into_any().unbind())
            } else if let Some(f) = n.as_f64() {
                Ok(pyo3::types::PyFloat::new(py, f).into_any().unbind())
            } else {
                Ok(py.None())
            }
        }
        serde_json::Value::String(s) => Ok(PyString::new(py, s).into_any().unbind()),
        serde_json::Value::Array(arr) => {
            let py_list = pyo3::types::PyList::empty(py);
            for item in arr {
                py_list.append(json_value_to_python(py, item)?)?;
            }
            Ok(py_list.into_any().unbind())
        }
        serde_json::Value::Object(obj) => {
            let py_dict = PyDict::new(py);
            for (key, val) in obj {
                py_dict.set_item(key, json_value_to_python(py, val)?)?;
            }
            Ok(py_dict.into_any().unbind())
        }
    }
}
