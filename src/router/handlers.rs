//! Route registration and matching system

use crate::request::RequestData;
use crate::response::ResponseData;
use http::Method;
use std::collections::HashMap;
use std::sync::Arc;

/// Trait for handling HTTP requests
pub trait RouteHandler: Send + Sync {
    fn handle(&self, req: RequestData) -> ResponseData;
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
    middleware: Vec<Arc<dyn super::middleware::Middleware>>,
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
        tracing::debug!("Adding route: {} {}", method, path);
        self.routes.insert((method, path), Arc::new(handler));
    }

    /// Add middleware to the router
    pub fn add_middleware<M>(&mut self, middleware: M)
    where
        M: super::middleware::Middleware + 'static,
    {
        tracing::debug!("Adding middleware");
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
        req: hyper::Request<hyper::body::Incoming>,
    ) -> Result<hyper::Response<http_body_util::Full<bytes::Bytes>>, hyper::Error> {
        // Convert Hyper request to our RequestData
        let request_data = match self.convert_request(req).await {
            Ok(data) => data,
            Err(err) => {
                tracing::warn!("Failed to convert request: {:?}", err);
                return Ok(self.error_response(hyper::StatusCode::BAD_REQUEST, "Bad Request"));
            }
        };

        // Process middleware (request phase)
        let mut req_data = request_data;
        for middleware in &self.middleware {
            if let Err(response) = middleware.process_request(&mut req_data) {
                return Ok(self.convert_response(response));
            }
        }

        // Find and execute route handler
        let key = (req_data.method.clone(), req_data.path.clone());
        let mut response_data = if let Some(handler) = self.routes.get(&key) {
            handler.handle(req_data.clone())
        } else {
            // Try pattern matching for dynamic routes
            if let Some(handler) = self.find_pattern_match(&req_data) {
                handler.handle(req_data.clone())
            } else {
                ResponseData {
                    status: hyper::StatusCode::NOT_FOUND,
                    headers: HashMap::new(),
                    body: b"Not Found".to_vec(),
                }
            }
        };

        // Process middleware (response phase)
        for middleware in &self.middleware {
            middleware
                .process_response(&req_data, &mut response_data);
        }

        Ok(self.convert_response(response_data))
    }

    /// Convert Hyper request to RequestData
    async fn convert_request(
        &self,
        req: hyper::Request<hyper::body::Incoming>,
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

        // Convert headers (optimized with pre-allocation)
        let mut headers = HashMap::with_capacity(parts.headers.len());
        for (k, v) in parts.headers.iter() {
            if let Ok(value_str) = v.to_str() {
                headers.insert(k.as_str().to_string(), value_str.to_string());
            }
        }

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
    ) -> hyper::Response<http_body_util::Full<bytes::Bytes>> {
        let mut builder = hyper::Response::builder().status(response.status);

        // Add headers
        for (key, value) in response.headers {
            builder = builder.header(key, value);
        }

        builder
            .body(http_body_util::Full::new(bytes::Bytes::from(response.body)))
            .unwrap_or_else(|_| {
                self.error_response(hyper::StatusCode::INTERNAL_SERVER_ERROR, "Internal Server Error")
            })
    }

    /// Create error response
    fn error_response(
        &self,
        status: hyper::StatusCode,
        message: &str,
    ) -> hyper::Response<http_body_util::Full<bytes::Bytes>> {
        hyper::Response::builder()
            .status(status)
            .header("content-type", "text/plain")
            .body(http_body_util::Full::new(bytes::Bytes::from(
                message.as_bytes().to_vec(),
            )))
            .unwrap()
    }

    /// Find pattern match for dynamic routes like /greet/<name> or /users/<int:id>
    fn find_pattern_match(&self, req: &RequestData) -> Option<Arc<dyn RouteHandler>> {
        super::matching::find_pattern_match(&self.routes, req)
    }
}

impl Default for Router {
    fn default() -> Self {
        Self::new()
    }
}

/// Simple function-based route handler
#[allow(dead_code)]
pub struct FunctionHandler<F> {
    func: F,
}

impl<F> FunctionHandler<F> {
    #[allow(dead_code)]
    pub fn new(func: F) -> Self {
        Self { func }
    }
}

impl<F> RouteHandler for FunctionHandler<F>
where
    F: Fn(RequestData) -> ResponseData + Send + Sync,
{
    fn handle(&self, req: RequestData) -> ResponseData {
        (self.func)(req)
    }
}