//! Middleware for request/response processing

use crate::request::RequestData;
use crate::response::ResponseData;
use http::Method;

/// Middleware trait for request/response processing
pub trait Middleware: Send + Sync {
    fn process_request(&self, req: &mut RequestData) -> Result<(), ResponseData>;
    fn process_response(&self, req: &RequestData, resp: &mut ResponseData);
}

/// CORS middleware implementation
#[allow(dead_code)]
pub struct CorsMiddleware {
    allowed_origins: Vec<String>,
    allowed_methods: Vec<Method>,
    allowed_headers: Vec<String>,
}

impl CorsMiddleware {
    #[allow(dead_code)]
    pub fn new() -> Self {
        Self {
            allowed_origins: vec!["*".to_string()],
            allowed_methods: vec![Method::GET, Method::POST, Method::PUT, Method::DELETE],
            allowed_headers: vec!["Content-Type".to_string(), "Authorization".to_string()],
        }
    }

    #[allow(dead_code)]
    pub fn with_origins(mut self, origins: Vec<String>) -> Self {
        self.allowed_origins = origins;
        self
    }
}

impl Default for CorsMiddleware {
    fn default() -> Self {
        Self::new()
    }
}

impl Middleware for CorsMiddleware {
    fn process_request(&self, _req: &mut RequestData) -> Result<(), ResponseData> {
        Ok(())
    }

    fn process_response(&self, _req: &RequestData, resp: &mut ResponseData) {
        // Add CORS headers
        resp.headers.insert(
            "Access-Control-Allow-Origin".to_string(),
            self.allowed_origins
                .first()
                .unwrap_or(&"*".to_string())
                .clone(),
        );

        resp.headers.insert(
            "Access-Control-Allow-Methods".to_string(),
            self.allowed_methods
                .iter()
                .map(|m| m.to_string())
                .collect::<Vec<_>>()
                .join(", "),
        );

        resp.headers.insert(
            "Access-Control-Allow-Headers".to_string(),
            self.allowed_headers.join(", "),
        );
    }
}
