//! Route registration and matching system

use crate::request::RequestData;
use crate::response::ResponseData;
use async_trait::async_trait;
use http::Method;
use hyper::{Request, Response, StatusCode};
use std::collections::HashMap;
use std::sync::Arc;
use tracing::{debug, warn};

/// Trait for handling HTTP requests
#[async_trait]
pub trait RouteHandler: Send + Sync {
    async fn handle(&self, req: RequestData) -> ResponseData;
}

/// Route information
#[allow(dead_code)]
pub struct Route {
    pub path: String,
    pub method: Method,
    pub handler: Arc<dyn RouteHandler>,
}

/// Router for managing routes and dispatching requests
pub struct Router {
    routes: HashMap<(Method, String), Arc<dyn RouteHandler>>,
    middleware: Vec<Arc<dyn Middleware>>,
}

/// Middleware trait for request/response processing
#[async_trait]
pub trait Middleware: Send + Sync {
    async fn process_request(&self, req: &mut RequestData) -> Result<(), ResponseData>;
    async fn process_response(&self, req: &RequestData, resp: &mut ResponseData);
}

impl Router {
    /// Create a new router
    pub fn new() -> Self {
        Self {
            routes: HashMap::new(),
            middleware: Vec::new(),
        }
    }

    /// Add a route to the router
    pub fn add_route<H>(&mut self, method: Method, path: String, handler: H)
    where
        H: RouteHandler + 'static,
    {
        debug!("Adding route: {} {}", method, path);
        self.routes.insert((method, path), Arc::new(handler));
    }

    /// Add middleware to the router
    pub fn add_middleware<M>(&mut self, middleware: M)
    where
        M: Middleware + 'static,
    {
        debug!("Adding middleware");
        self.middleware.push(Arc::new(middleware));
    }

    /// Get all registered routes (for debugging/inspection)
    pub fn get_routes(&self) -> Vec<(Method, String, Arc<dyn RouteHandler>)> {
        self.routes
            .iter()
            .map(|((method, path), handler)| (method.clone(), path.clone(), handler.clone()))
            .collect()
    }

    /// Get number of registered routes
    pub fn route_count(&self) -> usize {
        self.routes.len()
    }

    /// Handle incoming HTTP request
    pub async fn handle_request(
        &self,
        req: Request<hyper::body::Incoming>,
    ) -> Result<Response<http_body_util::Full<bytes::Bytes>>, hyper::Error> {
        // Convert Hyper request to our RequestData
        let request_data = match self.convert_request(req).await {
            Ok(data) => data,
            Err(err) => {
                warn!("Failed to convert request: {:?}", err);
                return Ok(self.error_response(StatusCode::BAD_REQUEST, "Bad Request"));
            }
        };

        // Process middleware (request phase)
        let mut req_data = request_data;
        for middleware in &self.middleware {
            if let Err(response) = middleware.process_request(&mut req_data).await {
                return Ok(self.convert_response(response));
            }
        }

        // Find and execute route handler
        let key = (req_data.method.clone(), req_data.path.clone());
        let mut response_data = if let Some(handler) = self.routes.get(&key) {
            handler.handle(req_data.clone()).await
        } else {
            // Try pattern matching for dynamic routes
            if let Some(handler) = self.find_pattern_match(&req_data) {
                handler.handle(req_data.clone()).await
            } else {
                ResponseData {
                    status: StatusCode::NOT_FOUND,
                    headers: HashMap::new(),
                    body: b"Not Found".to_vec(),
                }
            }
        };

        // Process middleware (response phase)
        for middleware in &self.middleware {
            middleware
                .process_response(&req_data, &mut response_data)
                .await;
        }

        Ok(self.convert_response(response_data))
    }

    /// Convert Hyper request to RequestData
    async fn convert_request(
        &self,
        req: Request<hyper::body::Incoming>,
    ) -> Result<RequestData, Box<dyn std::error::Error + Send + Sync>> {
        use http_body_util::BodyExt;

        let (parts, body) = req.into_parts();
        let body_bytes = body.collect().await?.to_bytes().to_vec();

        // Parse query parameters
        let query_params = parts
            .uri
            .query()
            .map(|query| {
                url::form_urlencoded::parse(query.as_bytes())
                    .into_owned()
                    .collect()
            })
            .unwrap_or_default();

        // Convert headers
        let headers = parts
            .headers
            .iter()
            .map(|(k, v)| (k.to_string(), v.to_str().unwrap_or("").to_string()))
            .collect();

        Ok(RequestData {
            method: parts.method,
            path: parts.uri.path().to_string(),
            query_string: parts.uri.query().unwrap_or("").to_string(),
            headers,
            body: body_bytes,
            query_params,
        })
    }

    /// Convert ResponseData to Hyper response
    fn convert_response(
        &self,
        response: ResponseData,
    ) -> Response<http_body_util::Full<bytes::Bytes>> {
        let mut builder = Response::builder().status(response.status);

        // Add headers
        for (key, value) in response.headers {
            builder = builder.header(key, value);
        }

        builder
            .body(http_body_util::Full::new(bytes::Bytes::from(response.body)))
            .unwrap_or_else(|_| {
                self.error_response(StatusCode::INTERNAL_SERVER_ERROR, "Internal Server Error")
            })
    }

    /// Create error response
    fn error_response(
        &self,
        status: StatusCode,
        message: &str,
    ) -> Response<http_body_util::Full<bytes::Bytes>> {
        Response::builder()
            .status(status)
            .header("content-type", "text/plain")
            .body(http_body_util::Full::new(bytes::Bytes::from(
                message.as_bytes().to_vec(),
            )))
            .unwrap()
    }

    /// Find pattern match for dynamic routes like /greet/<name> or /users/<int:id>
    fn find_pattern_match(&self, req: &RequestData) -> Option<Arc<dyn RouteHandler>> {
        // Normalize path segments
        let req_parts: Vec<&str> = req.path.trim_matches('/').split('/').collect();

        for ((method, pattern), handler) in self.routes.iter() {
            if method != req.method {
                continue;
            }

            // Skip non-pattern routes here (they are handled by exact match earlier)
            if !pattern.contains('<') || !pattern.contains('>') {
                continue;
            }

            let pat_parts: Vec<&str> = pattern.trim_matches('/').split('/').collect();
            if pat_parts.len() != req_parts.len() {
                continue;
            }

            let mut matched = true;

            for (pp, rp) in pat_parts.iter().zip(req_parts.iter()) {
                if pp.starts_with('<') && pp.ends_with('>') {
                    // Pattern segment, optionally typed like <int:id> or just <name>
                    let inner = &pp[1..pp.len() - 1];
                    let (typ, _name) = if let Some((t, n)) = inner.split_once(':') {
                        (t.trim(), n.trim())
                    } else {
                        ("str", inner.trim())
                    };

                    // Minimal type checks
                    match typ {
                        "int" => {
                            if rp.parse::<i64>().is_err() {
                                matched = false;
                                break;
                            }
                        }
                        // Accept any non-empty string for str/float/path/etc. for now
                        _ => {
                            if rp.is_empty() {
                                matched = false;
                                break;
                            }
                        }
                    }
                } else if pp != rp {
                    matched = false;
                    break;
                }
            }

            if matched {
                return Some(handler.clone());
            }
        }

        None
    }
}

impl Default for Router {
    fn default() -> Self {
        Self::new()
    }
}

/// Simple function-based route handler
pub struct FunctionHandler<F> {
    func: F,
}

impl<F> FunctionHandler<F> {
    pub fn new(func: F) -> Self {
        Self { func }
    }
}

#[async_trait]
impl<F, Fut> RouteHandler for FunctionHandler<F>
where
    F: Fn(RequestData) -> Fut + Send + Sync,
    Fut: std::future::Future<Output = ResponseData> + Send,
{
    async fn handle(&self, req: RequestData) -> ResponseData {
        (self.func)(req).await
    }
}

/// CORS middleware implementation
pub struct CorsMiddleware {
    allowed_origins: Vec<String>,
    allowed_methods: Vec<Method>,
    allowed_headers: Vec<String>,
}

impl CorsMiddleware {
    pub fn new() -> Self {
        Self {
            allowed_origins: vec!["*".to_string()],
            allowed_methods: vec![Method::GET, Method::POST, Method::PUT, Method::DELETE],
            allowed_headers: vec!["Content-Type".to_string(), "Authorization".to_string()],
        }
    }

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

#[async_trait]
impl Middleware for CorsMiddleware {
    async fn process_request(&self, _req: &mut RequestData) -> Result<(), ResponseData> {
        Ok(())
    }

    async fn process_response(&self, _req: &RequestData, resp: &mut ResponseData) {
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_router_creation() {
        let router = Router::new();
        assert_eq!(router.routes.len(), 0);
        assert_eq!(router.middleware.len(), 0);
    }
}
