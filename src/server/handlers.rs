//! Actix-web HTTP Server implementation for maximum performance

use actix_web::{web, HttpRequest, HttpResponse};
use std::sync::Arc;
use tokio::sync::RwLock;

/// Configuration for the BustAPI server
#[derive(Debug, Clone)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
    pub debug: bool,
    pub workers: usize,
}

impl Default for ServerConfig {
    fn default() -> Self {
        Self {
            host: "127.0.0.1".to_string(),
            port: 5000,
            debug: false,
            workers: num_cpus::get(),
        }
    }
}

/// Route handler trait for polymorphic handlers
pub trait RouteHandler: Send + Sync + 'static {
    fn handle(&self, req: &HttpRequest, body: web::Bytes) -> HttpResponse;
}

/// Storage for routes
pub struct RouteStorage {
    routes: std::collections::HashMap<(String, String), Arc<dyn RouteHandler>>,
}

impl RouteStorage {
    pub fn new() -> Self {
        Self {
            routes: std::collections::HashMap::new(),
        }
    }

    pub fn add_route<H: RouteHandler>(&mut self, method: &str, path: &str, handler: H) {
        let key = (method.to_uppercase(), path.to_string());
        self.routes.insert(key, Arc::new(handler));
    }

    pub fn get_handler(&self, method: &str, path: &str) -> Option<Arc<dyn RouteHandler>> {
        let key = (method.to_uppercase(), path.to_string());
        self.routes.get(&key).cloned()
    }
}

impl Default for RouteStorage {
    fn default() -> Self {
        Self::new()
    }
}

/// Fast route handler that returns static response (no Python needed)
pub struct FastRouteHandler {
    response_body: String,
    content_type: String,
}

impl FastRouteHandler {
    pub fn new(response_body: String) -> Self {
        Self {
            response_body,
            content_type: "application/json".to_string(),
        }
    }

    pub fn with_content_type(mut self, content_type: &str) -> Self {
        self.content_type = content_type.to_string();
        self
    }
}

impl RouteHandler for FastRouteHandler {
    fn handle(&self, _req: &HttpRequest, _body: web::Bytes) -> HttpResponse {
        HttpResponse::Ok()
            .content_type(self.content_type.clone())
            .body(self.response_body.clone())
    }
}

/// Shared application state
pub struct AppState {
    pub routes: RwLock<RouteStorage>,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            routes: RwLock::new(RouteStorage::new()),
        }
    }
}

impl Default for AppState {
    fn default() -> Self {
        Self::new()
    }
}

/// Main request handler - dispatches to registered route handlers
pub async fn handle_request(
    req: HttpRequest,
    body: web::Bytes,
    state: web::Data<Arc<AppState>>,
) -> HttpResponse {
    let method = req.method().as_str();
    let path = req.path();

    // Get handler from routes
    let routes = state.routes.read().await;
    if let Some(handler) = routes.get_handler(method, path) {
        drop(routes); // Release lock before handling
        handler.handle(&req, body)
    } else {
        HttpResponse::NotFound()
            .content_type("application/json")
            .body(r#"{"error": "Not Found"}"#)
    }
}
