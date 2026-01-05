//! Conversion utilities between Python and Rust types

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyString, PyTuple};
use std::collections::HashMap;

/// Convert Python result to ResponseData
pub fn convert_py_result_to_response(
    py: Python,
    result: PyObject,
) -> crate::response::ResponseData {
    use crate::response::ResponseData;
    use http::StatusCode;

    // Check if tuple (body, status) or (body, status, headers)
    if let Ok(tuple) = result.downcast_bound::<PyTuple>(py) {
        match tuple.len() {
            2 => {
                if let (Ok(body), Ok(status)) = (
                    tuple.get_item(0),
                    tuple.get_item(1).and_then(|s| s.extract::<u16>()),
                ) {
                    let response_body = python_to_response_body(py, body.into());
                    let mut resp = ResponseData::with_body(response_body.into_bytes());
                    resp.set_status(StatusCode::from_u16(status).unwrap_or(StatusCode::OK));
                    resp.set_header("Content-Type", "text/html; charset=utf-8"); // Default to HTML for tuples? Or JSON?
                    // Previous code defaulted to JSON. Let's keep JSON for tuples unless specified.
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
                         if let Ok(iter) = items.bind(py).iter() {
                             for item_res in iter {
                                 if let Ok(item) = item_res {
                                     // Extract tuple (key, value)
                                     if let Ok((k, v)) = item.extract::<(String, String)>() {
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

/// Convert Python object to response body bytes
pub fn python_to_response_body(py: Python, obj: PyObject) -> String {
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
#[allow(deprecated)]
pub fn json_value_to_python(py: Python, value: &serde_json::Value) -> PyResult<PyObject> {
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
