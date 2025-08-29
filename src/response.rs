//! HTTP Response data structures and utilities

use hyper::StatusCode;
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
        // Avoid needless borrow on generic arg
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

    /// Set response status
    pub fn set_status(&mut self, status: StatusCode) -> &mut Self {
        self.status = status;
        self
    }

    /// Set response body
    pub fn set_body<B: Into<Vec<u8>>>(&mut self, body: B) -> &mut Self {
        self.body = body.into();
        self
    }

    /// Set response body as string
    pub fn set_body_string<S: Into<String>>(&mut self, body: S) -> &mut Self {
        self.body = body.into().into_bytes();
        self
    }

    /// Set response body as JSON
    pub fn set_body_json<T: serde::Serialize>(
        &mut self,
        data: &T,
    ) -> Result<&mut Self, serde_json::Error> {
        let json_string = serde_json::to_string(data)?;
        self.body = json_string.into_bytes();
        self.set_header("Content-Type", "application/json");
        Ok(self)
    }

    /// Set header value
    pub fn set_header<K: Into<String>, V: Into<String>>(&mut self, key: K, value: V) -> &mut Self {
        self.headers.insert(key.into(), value.into());
        self
    }

    /// Get header value
    pub fn get_header(&self, key: &str) -> Option<&String> {
        self.headers.get(key)
    }

    /// Remove header
    pub fn remove_header(&mut self, key: &str) -> Option<String> {
        self.headers.remove(key)
    }

    /// Add cookie to response
    pub fn set_cookie(&mut self, name: &str, value: &str, options: CookieOptions) -> &mut Self {
        let cookie = format_cookie(name, value, options);
        self.headers.insert("Set-Cookie".to_string(), cookie);
        self
    }

    /// Get response body as string
    pub fn body_as_string(&self) -> Result<String, std::string::FromUtf8Error> {
        String::from_utf8(self.body.clone())
    }

    /// Get response body as JSON
    pub fn body_as_json<T>(&self) -> Result<T, serde_json::Error>
    where
        T: serde::de::DeserializeOwned,
    {
        serde_json::from_slice(&self.body)
    }

    /// Check if response is successful (2xx status)
    pub fn is_success(&self) -> bool {
        self.status.is_success()
    }

    /// Check if response is redirect (3xx status)
    pub fn is_redirect(&self) -> bool {
        self.status.is_redirection()
    }

    /// Check if response is client error (4xx status)
    pub fn is_client_error(&self) -> bool {
        self.status.is_client_error()
    }

    /// Check if response is server error (5xx status)
    pub fn is_server_error(&self) -> bool {
        self.status.is_server_error()
    }

    /// Get content length
    pub fn content_length(&self) -> usize {
        self.body.len()
    }

    /// Set content length header
    pub fn set_content_length(&mut self) -> &mut Self {
        self.set_header("Content-Length", self.content_length().to_string())
    }
}

impl Default for ResponseData {
    fn default() -> Self {
        Self::new()
    }
}

/// Cookie options for setting cookies
#[derive(Debug, Clone)]
pub struct CookieOptions {
    pub max_age: Option<i64>,
    pub expires: Option<String>,
    pub domain: Option<String>,
    pub path: Option<String>,
    pub secure: bool,
    pub http_only: bool,
    pub same_site: Option<SameSite>,
}

impl Default for CookieOptions {
    fn default() -> Self {
        Self {
            max_age: None,
            expires: None,
            domain: None,
            path: Some("/".to_string()),
            secure: false,
            http_only: true,
            same_site: None,
        }
    }
}

#[derive(Debug, Clone)]
pub enum SameSite {
    Strict,
    Lax,
    None,
}

impl SameSite {
    fn as_str(&self) -> &'static str {
        match self {
            SameSite::Strict => "Strict",
            SameSite::Lax => "Lax",
            SameSite::None => "None",
        }
    }
}

/// Format cookie string with options
fn format_cookie(name: &str, value: &str, options: CookieOptions) -> String {
    let mut cookie = format!("{}={}", name, value);

    if let Some(max_age) = options.max_age {
        cookie.push_str(&format!("; Max-Age={}", max_age));
    }

    if let Some(expires) = options.expires {
        cookie.push_str(&format!("; Expires={}", expires));
    }

    if let Some(domain) = options.domain {
        cookie.push_str(&format!("; Domain={}", domain));
    }

    if let Some(path) = options.path {
        cookie.push_str(&format!("; Path={}", path));
    }

    if options.secure {
        cookie.push_str("; Secure");
    }

    if options.http_only {
        cookie.push_str("; HttpOnly");
    }

    if let Some(same_site) = options.same_site {
        cookie.push_str(&format!("; SameSite={}", same_site.as_str()));
    }

    cookie
}

// Convenience functions for common responses

/// Create OK response
#[allow(dead_code)]
pub fn ok() -> ResponseData {
    ResponseData::with_status(StatusCode::OK)
}

/// Create Not Found response
#[allow(dead_code)]
pub fn not_found() -> ResponseData {
    ResponseData::error(StatusCode::NOT_FOUND, Some("Not Found"))
}

/// Create Internal Server Error response
#[allow(dead_code)]
pub fn internal_server_error() -> ResponseData {
    ResponseData::error(
        StatusCode::INTERNAL_SERVER_ERROR,
        Some("Internal Server Error"),
    )
}

/// Create Bad Request response
#[allow(dead_code)]
pub fn bad_request(message: Option<&str>) -> ResponseData {
    ResponseData::error(StatusCode::BAD_REQUEST, message)
}

/// Create Unauthorized response
#[allow(dead_code)]
pub fn unauthorized() -> ResponseData {
    ResponseData::error(StatusCode::UNAUTHORIZED, Some("Unauthorized"))
}

/// Create Forbidden response
#[allow(dead_code)]
pub fn forbidden() -> ResponseData {
    ResponseData::error(StatusCode::FORBIDDEN, Some("Forbidden"))
}

/// Create JSON response from serializable data
pub fn json<T: serde::Serialize>(data: &T) -> Result<ResponseData, serde_json::Error> {
    ResponseData::json(data)
}

/// Create HTML response
pub fn html<S: Into<String>>(content: S) -> ResponseData {
    ResponseData::html(content)
}

/// Create text response
pub fn text<S: Into<String>>(content: S) -> ResponseData {
    ResponseData::text(content)
}

/// Create redirect response
pub fn redirect<S: Into<String>>(url: S) -> ResponseData {
    ResponseData::redirect(url, false)
}

/// Create permanent redirect response
pub fn redirect_permanent<S: Into<String>>(url: S) -> ResponseData {
    ResponseData::redirect(url, true)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_response_creation() {
        let resp = ResponseData::new();
        assert_eq!(resp.status, StatusCode::OK);
        assert!(resp.headers.is_empty());
        assert!(resp.body.is_empty());
    }

    #[test]
    fn test_json_response() {
        let data = json!({"message": "Hello, World!"});
        let resp = ResponseData::json(&data).unwrap();

        assert_eq!(resp.status, StatusCode::OK);
        assert_eq!(
            resp.get_header("Content-Type"),
            Some(&"application/json".to_string())
        );

        let body_str = resp.body_as_string().unwrap();
        assert!(body_str.contains("Hello, World!"));
    }

    #[test]
    fn test_redirect_response() {
        let resp = ResponseData::redirect("/new-path", false);
        assert_eq!(resp.status, StatusCode::FOUND);
        assert_eq!(resp.get_header("Location"), Some(&"/new-path".to_string()));
    }

    #[test]
    fn test_cookie_formatting() {
        let options = CookieOptions {
            max_age: Some(3600),
            secure: true,
            http_only: true,
            same_site: Some(SameSite::Strict),
            ..Default::default()
        };

        let cookie = format_cookie("session", "abc123", options);
        assert_eq!(
            cookie,
            "session=abc123; Max-Age=3600; Path=/; Secure; HttpOnly; SameSite=Strict"
        );
    }
}
