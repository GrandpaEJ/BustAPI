//! HTTP Request data structures and utilities

use http::Method;
use std::collections::HashMap;

/// Represents an uploaded file
#[derive(Debug, Clone)]
pub struct UploadedFile {
    pub filename: String,
    pub content_type: String,
    pub content: Vec<u8>,
}

/// HTTP request data structure
#[derive(Debug, Clone)]
pub struct RequestData {
    pub method: Method,
    pub path: String,
    pub query_string: String,
    pub headers: HashMap<String, String>,
    pub body: Vec<u8>,
    pub query_params: HashMap<String, String>,
    pub files: HashMap<String, UploadedFile>,
    pub multipart_form: HashMap<String, String>,
}

impl RequestData {
    /// Create a new RequestData instance
    pub fn new(method: Method, path: String) -> Self {
        Self {
            method,
            path,
            query_string: String::new(),
            headers: HashMap::new(),
            body: Vec::new(),
            query_params: HashMap::new(),
            files: HashMap::new(),
            multipart_form: HashMap::new(),
        }
    }

    /// Get the request method as a string
    pub fn method_str(&self) -> &str {
        self.method.as_str()
    }

    /// Get a header value by name (case-insensitive)
    pub fn get_header(&self, name: &str) -> Option<&String> {
        let name_lower = name.to_lowercase();
        self.headers
            .iter()
            .find(|(k, _)| k.to_lowercase() == name_lower)
            .map(|(_, v)| v)
    }

    /// Get query parameter value by name
    pub fn get_query_param(&self, name: &str) -> Option<&String> {
        self.query_params.get(name)
    }

    /// Get request body as string (assuming UTF-8)
    pub fn body_as_string(&self) -> Result<String, std::string::FromUtf8Error> {
        String::from_utf8(self.body.clone())
    }

    /// Get request body as JSON
    pub fn body_as_json<T>(&self) -> Result<T, serde_json::Error>
    where
        T: serde::de::DeserializeOwned,
    {
        serde_json::from_slice(&self.body)
    }

    /// Check if request has JSON content type
    pub fn is_json(&self) -> bool {
        self.get_header("content-type")
            .map(|ct| ct.to_lowercase().contains("application/json"))
            .unwrap_or(false)
    }

    /// Check if request has form data content type
    pub fn is_form(&self) -> bool {
        self.get_header("content-type")
            .map(|ct| {
                ct.to_lowercase()
                    .contains("application/x-www-form-urlencoded")
            })
            .unwrap_or(false)
    }

    /// Parse form data from body
    pub fn parse_form_data(&self) -> HashMap<String, String> {
        if !self.is_form() {
            return HashMap::new();
        }

        match self.body_as_string() {
            Ok(body_str) => url::form_urlencoded::parse(body_str.as_bytes())
                .into_owned()
                .collect(),
            Err(_) => HashMap::new(),
        }
    }

    /// Get cookies from request headers
    pub fn get_cookies(&self) -> HashMap<String, String> {
        let mut cookies = HashMap::new();

        if let Some(cookie_header) = self.get_header("cookie") {
            for cookie_pair in cookie_header.split(';') {
                let cookie_pair = cookie_pair.trim();
                if let Some((key, value)) = cookie_pair.split_once('=') {
                    cookies.insert(key.trim().to_string(), value.trim().to_string());
                }
            }
        }

        cookies
    }

    /// Check if request is HTTPS
    pub fn is_secure(&self) -> bool {
        self.get_header("x-forwarded-proto")
            .map(|proto| proto == "https")
            .unwrap_or(false)
            || self
                .get_header("x-forwarded-ssl")
                .map(|ssl| ssl == "on")
                .unwrap_or(false)
    }

    /// Get client IP address
    pub fn client_ip(&self) -> Option<String> {
        // Check common proxy headers first
        if let Some(forwarded_for) = self.get_header("x-forwarded-for") {
            if let Some(first_ip) = forwarded_for.split(',').next() {
                return Some(first_ip.trim().to_string());
            }
        }

        if let Some(real_ip) = self.get_header("x-real-ip") {
            return Some(real_ip.clone());
        }

        // TODO: Get from connection info when available
        None
    }

    /// Get user agent
    pub fn user_agent(&self) -> Option<&String> {
        self.get_header("user-agent")
    }

    /// Check if request accepts JSON response
    pub fn accepts_json(&self) -> bool {
        self.get_header("accept")
            .map(|accept| accept.to_lowercase().contains("application/json"))
            .unwrap_or(false)
    }

    /// Check if request accepts HTML response
    pub fn accepts_html(&self) -> bool {
        self.get_header("accept")
            .map(|accept| accept.to_lowercase().contains("text/html"))
            .unwrap_or(false)
    }
}

impl Default for RequestData {
    fn default() -> Self {
        Self::new(Method::GET, "/".to_string())
    }
}
