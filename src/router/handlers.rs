//! Route registration and matching system
//!
//! Uses matchit radix tree for O(log n) route matching instead of O(n) linear iteration.

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

/// Handler wrapper that stores the handler and original path pattern
struct HandlerEntry {
    handler: Arc<dyn RouteHandler>,
    #[allow(dead_code)]
    original_pattern: String,
}

/// Convert BustAPI path pattern to matchit format
/// <name> -> {name}
/// <int:id> -> {id}
/// <float:val> -> {val}
/// <path:rest> -> {*rest}
fn convert_pattern_to_matchit(pattern: &str) -> String {
    let mut result = String::with_capacity(pattern.len());
    let mut chars = pattern.chars().peekable();
    
    while let Some(c) = chars.next() {
        if c == '<' {
            // Find the closing >
            let mut param = String::new();
            while let Some(&nc) = chars.peek() {
                if nc == '>' {
                    chars.next(); // consume '>'
                    break;
                }
                param.push(chars.next().unwrap());
            }
            
            // Parse the parameter: type:name or just name
            let (param_type, param_name) = if let Some((t, n)) = param.split_once(':') {
                (t.trim(), n.trim())
            } else {
                ("str", param.trim())
            };
            
            // Convert to matchit syntax
            if param_type == "path" {
                // Wildcard/catch-all parameter
                result.push_str("{*");
                result.push_str(param_name);
                result.push('}');
            } else {
                // Regular parameter (int, float, str all become the same in matchit)
                result.push('{');
                result.push_str(param_name);
                result.push('}');
            }
        } else {
            result.push(c);
        }
    }
    
    result
}

/// Router for managing routes and dispatching requests
/// Uses matchit radix tree for O(log n) route matching
pub struct Router {
    /// Matchit routers per HTTP method for fast lookup
    method_routers: HashMap<Method, matchit::Router<usize>>,
    /// Handler storage indexed by ID
    handlers: Vec<HandlerEntry>,
    /// Legacy routes map for redirect slash checking (static routes only)
    pub(crate) routes: HashMap<(Method, String), Arc<dyn RouteHandler>>,
    pub(crate) middleware: Vec<Arc<dyn super::middleware::Middleware>>,
    pub(crate) redirect_slashes: bool,
}

impl Router {
    /// Create a new router
    pub fn new() -> Self {
        Self {
            method_routers: HashMap::new(),
            handlers: Vec::new(),
            routes: HashMap::new(),
            middleware: Vec::new(),
            redirect_slashes: true,
        }
    }

    /// Add a route to the router
    pub fn add_route<H>(&mut self, method: Method, path: String, handler: H)
    where
        H: RouteHandler + 'static,
    {
        tracing::debug!("Adding route: {} {}", method, path);
        
        let handler_arc = Arc::new(handler);
        let handler_id = self.handlers.len();
        
        // Store handler
        self.handlers.push(HandlerEntry {
            handler: handler_arc.clone(),
            original_pattern: path.clone(),
        });
        
        // Also store in legacy routes map for compatibility
        self.routes.insert((method.clone(), path.clone()), handler_arc);
        
        // Convert pattern to matchit format
        let matchit_pattern = convert_pattern_to_matchit(&path);
        
        // Get or create method router
        let method_router = self.method_routers
            .entry(method)
            .or_insert_with(matchit::Router::new);
        
        // Insert route (ignore errors for duplicate routes)
        if let Err(e) = method_router.insert(&matchit_pattern, handler_id) {
            tracing::warn!("Route insertion warning for {}: {:?}", matchit_pattern, e);
        }
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
        self.handlers.len()
    }

    /// Process incoming request through middleware and handlers
    pub fn process_request(&self, request_data: RequestData) -> ResponseData {
        // Process middleware (request phase)
        let mut req_data = request_data;
        for middleware in &self.middleware {
            if let Err(response) = middleware.process_request(&mut req_data) {
                return response;
            }
        }

        // Try to match using matchit radix tree (O(log n))
        let handler_opt = self.match_route(&req_data).or_else(|| {
            // HEAD -> GET fallback
            if req_data.method == Method::HEAD {
                let mut get_req = req_data.clone();
                get_req.method = Method::GET;
                self.match_route(&get_req)
            } else {
                None
            }
        });

        let mut response_data = if let Some(handler) = handler_opt {
            handler.handle(req_data.clone())
        } else {
            // Not found - check for redirect if enabled
            self.try_redirect(&req_data).unwrap_or_else(|| {
                ResponseData::error(http::StatusCode::NOT_FOUND, Some("Not Found"))
            })
        };

        // Process middleware (response phase)
        for middleware in &self.middleware {
            middleware.process_response(&req_data, &mut response_data);
        }

        response_data
    }

    /// Match a route using matchit radix tree
    fn match_route(&self, req: &RequestData) -> Option<Arc<dyn RouteHandler>> {
        let method_router = self.method_routers.get(&req.method)?;
        let matched = method_router.at(&req.path).ok()?;
        let handler_id = *matched.value;
        Some(self.handlers[handler_id].handler.clone())
    }

    /// Try to redirect with/without trailing slash
    fn try_redirect(&self, req_data: &RequestData) -> Option<ResponseData> {
        if !self.redirect_slashes {
            return None;
        }

        let path = &req_data.path;
        let method = &req_data.method;

        // Check redirect for current method
        let redirect_path = if path.ends_with('/') {
            let trimmed = &path[..path.len() - 1];
            if self.routes.contains_key(&(method.clone(), trimmed.to_string())) {
                Some(trimmed.to_string())
            } else {
                None
            }
        } else {
            let slashed = format!("{}/", path);
            if self.routes.contains_key(&(method.clone(), slashed.clone())) {
                Some(slashed)
            } else {
                None
            }
        };

        // HEAD -> GET fallback for redirect
        let redirect_path = redirect_path.or_else(|| {
            if *method == Method::HEAD {
                let get_method = Method::GET;
                if path.ends_with('/') {
                    let trimmed = &path[..path.len() - 1];
                    if self.routes.contains_key(&(get_method.clone(), trimmed.to_string())) {
                        return Some(trimmed.to_string());
                    }
                } else {
                    let slashed = format!("{}/", path);
                    if self.routes.contains_key(&(get_method.clone(), slashed.clone())) {
                        return Some(slashed);
                    }
                }
            }
            None
        });

        redirect_path.map(|new_path| {
            let mut resp = ResponseData::new();
            resp.status = http::StatusCode::TEMPORARY_REDIRECT;
            let location = if !req_data.query_string.is_empty() {
                format!("{}?{}", new_path, req_data.query_string)
            } else {
                new_path
            };
            resp.headers.insert("Location".to_string(), location);
            resp
        })
    }

    /// Find pattern match for dynamic routes (legacy method for compatibility)
    /// Now uses matchit internally
    #[allow(dead_code)]
    fn find_pattern_match(&self, req: &RequestData) -> Option<Arc<dyn RouteHandler>> {
        self.match_route(req)
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pattern_conversion() {
        assert_eq!(convert_pattern_to_matchit("/users/<id>"), "/users/{id}");
        assert_eq!(convert_pattern_to_matchit("/users/<int:id>"), "/users/{id}");
        assert_eq!(convert_pattern_to_matchit("/files/<path:rest>"), "/files/{*rest}");
        assert_eq!(convert_pattern_to_matchit("/api/<version>/users/<int:id>"), "/api/{version}/users/{id}");
    }
}
