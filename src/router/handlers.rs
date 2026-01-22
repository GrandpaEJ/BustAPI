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
    pub(crate) routes: HashMap<(Method, String), Arc<dyn RouteHandler>>,
    pub(crate) middleware: Vec<Arc<dyn super::middleware::Middleware>>,
    pub(crate) redirect_slashes: bool,
}

impl Router {
    /// Create a new router
    pub fn new() -> Self {
        Self {
            routes: HashMap::new(),
            middleware: Vec::new(),
            redirect_slashes: true, // Default to true (Safe Bidirectional)
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
    #[allow(dead_code)]
    pub fn add_middleware<M>(&mut self, middleware: M)
    where
        M: super::middleware::Middleware + 'static,
    {
        tracing::debug!("Adding middleware");
        self.middleware.push(Arc::new(middleware));
    }

    /// Get all registered routes (for debugging/inspection)
    #[allow(dead_code)]
    pub fn get_routes(&self) -> Vec<(Method, String, Arc<dyn RouteHandler>)> {
        self.routes
            .iter()
            .map(|((method, path), handler)| (method.clone(), path.clone(), handler.clone()))
            .collect()
    }

    /// Get number of registered routes
    #[allow(dead_code)]
    pub fn route_count(&self) -> usize {
        self.routes.len()
    }

    /// Process incoming request through middleware and handlers
    pub fn process_request(&self, request_data: RequestData) -> ResponseData {
        // Process middleware (request phase)
        let mut req_data = request_data;
        for middleware in &self.middleware {
            // Middleware process_request returns properties referencing req_data if we are not careful.
            // But here process_request takes &mut RequestData and returns Result<(), ResponseData>
            if let Err(response) = middleware.process_request(&mut req_data) {
                return response;
            }
        }

        // Find and execute route handler
        let key = (req_data.method.clone(), req_data.path.clone());
        let mut response_data = if let Some(handler) = self.routes.get(&key) {
            handler.handle(req_data.clone())
        } else {
            // Check for HEAD -> GET fallback
            let mut handler_found = None;

            if req_data.method == Method::HEAD {
                let get_key = (Method::GET, req_data.path.clone());
                if let Some(handler) = self.routes.get(&get_key) {
                    handler_found = Some(handler.clone());
                }
            }

            if let Some(handler) = handler_found {
                handler.handle(req_data.clone())
            } else {
                // Try pattern matching for dynamic routes
                let match_result = self.find_pattern_match(&req_data).or_else(|| {
                    // If HEAD request, try matching against GET routes
                    if req_data.method == Method::HEAD {
                        // Create temporary request data with GET method for matching
                        let mut get_req = req_data.clone();
                        get_req.method = Method::GET;
                        self.find_pattern_match(&get_req)
                    } else {
                        None
                    }
                });

                if let Some(handler) = match_result {
                    handler.handle(req_data.clone())
                } else {
                    // Not found. Check for redirect if enabled
                    let mut redirect_path: Option<String> = None;

                    if self.redirect_slashes {
                        let path = &req_data.path;
                        let method = &req_data.method;

                        // Check redirect for current method
                        if path.ends_with('/') {
                            let trimmed = &path[..path.len() - 1];
                            if self
                                .routes
                                .contains_key(&(method.clone(), trimmed.to_string()))
                            {
                                redirect_path = Some(trimmed.to_string());
                            }
                        } else {
                            let slashed = format!("{}/", path);
                            if self.routes.contains_key(&(method.clone(), slashed.clone())) {
                                redirect_path = Some(slashed);
                            }
                        }

                        // Check redirect for GET (fallback for HEAD)
                        if redirect_path.is_none() && *method == Method::HEAD {
                            let get_method = Method::GET;
                            if path.ends_with('/') {
                                let trimmed = &path[..path.len() - 1];
                                if self
                                    .routes
                                    .contains_key(&(get_method.clone(), trimmed.to_string()))
                                {
                                    redirect_path = Some(trimmed.to_string());
                                }
                            } else {
                                let slashed = format!("{}/", path);
                                if self
                                    .routes
                                    .contains_key(&(get_method.clone(), slashed.clone()))
                                {
                                    redirect_path = Some(slashed);
                                }
                            }
                        }
                    }

                    if let Some(new_path) = redirect_path {
                        // Create 307 Temporary Redirect response
                        let mut resp = ResponseData::new();
                        resp.status = http::StatusCode::TEMPORARY_REDIRECT;

                        // Preserve query string
                        let location = if !req_data.query_string.is_empty() {
                            format!("{}?{}", new_path, req_data.query_string)
                        } else {
                            new_path
                        };

                        resp.headers.insert("Location".to_string(), location);
                        resp
                    } else {
                        ResponseData::error(http::StatusCode::NOT_FOUND, Some("Not Found"))
                    }
                }
            }
        };

        // Process middleware (response phase)
        for middleware in &self.middleware {
            middleware.process_response(&req_data, &mut response_data);
        }

        response_data
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
