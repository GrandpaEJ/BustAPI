//! HTTP Response data structures and utilities

use http::StatusCode;
use std::collections::HashMap;

/// HTTP response data structure
#[derive(Debug, Clone)]
pub struct ResponseData {
    pub status: StatusCode,
    pub headers: HashMap<String, String>,
    pub body: Vec<u8>,
}

impl ResponseData {
    /// Create a new ResponseData instance
    pub fn new() -> Self {
        Self {
            status: StatusCode::OK,
            headers: HashMap::new(),
            body: Vec::new(),
        }
    }

    /// Create response from static bytes (zero-copy)
    pub fn from_static(body: &'static [u8]) -> Self {
        Self {
            status: StatusCode::OK,
            headers: HashMap::new(),
            body: body.to_vec(),
        }
    }

    /// Create JSON response with pre-serialized content
    pub fn json_static(json: &'static str) -> Self {
        let mut headers = HashMap::new();
        headers.insert("Content-Type".to_string(), "application/json".to_string());
        Self {
            status: StatusCode::OK,
            headers,
            body: json.as_bytes().to_vec(),
        }
    }

    /// Create response with status code
    pub fn with_status(status: StatusCode) -> Self {
        Self {
            status,
            headers: HashMap::new(),
            body: Vec::new(),
        }
    }

    /// Create response with body
    pub fn with_body<B: Into<Vec<u8>>>(body: B) -> Self {
        Self {
            status: StatusCode::OK,
            headers: HashMap::new(),
            body: body.into(),
        }
    }

    /// Create JSON response
    pub fn json<T: serde::Serialize>(data: &T) -> Result<Self, serde_json::Error> {
        let json_string = serde_json::to_string(data)?;
        let mut response = Self::with_body(json_string.into_bytes());
        response.set_header("Content-Type", "application/json");
        Ok(response)
    }

    /// Create HTML response
    pub fn html<S: Into<String>>(html: S) -> Self {
        let mut response = Self::with_body(html.into().into_bytes());
        response.set_header("Content-Type", "text/html; charset=utf-8");
        response
    }

    /// Create plain text response
    pub fn text<S: Into<String>>(text: S) -> Self {
        let mut response = Self::with_body(text.into().into_bytes());
        response.set_header("Content-Type", "text/plain; charset=utf-8");
        response
    }

    /// Create redirect response
    pub fn redirect<S: Into<String>>(url: S, permanent: bool) -> Self {
        let status = if permanent {
            StatusCode::MOVED_PERMANENTLY
        } else {
            StatusCode::FOUND
        };

        let mut response = Self::with_status(status);
        response.set_header("Location", url.into());
        response
    }

    /// Create error response
    pub fn error(status: StatusCode, message: Option<&str>) -> Self {
        let body = message
            .unwrap_or(status.canonical_reason().unwrap_or("Unknown Error"))
            .to_string();

        let mut response = Self::with_status(status);
        response.set_body(body.into_bytes());
        response.set_header("Content-Type", "text/plain; charset=utf-8");
        response
    }
}

impl Default for ResponseData {
    fn default() -> Self {
        Self::new()
    }
}
