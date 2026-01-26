//! Actix-web HTTP Server implementation for maximum performance

use actix_multipart::Multipart;
use actix_web::{web, HttpRequest, HttpResponse};
use futures::{StreamExt, TryStreamExt};
use std::sync::Arc;
use tokio::sync::RwLock;

use crate::request::RequestData;
use crate::router::{RouteHandler, Router};
use std::time::Instant;

/// Configuration for the BustAPI server
#[derive(Debug, Clone)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
    #[allow(dead_code)]
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

    #[allow(dead_code)]
    pub fn with_content_type(mut self, content_type: &str) -> Self {
        self.content_type = content_type.to_string();
        self
    }
}

impl RouteHandler for FastRouteHandler {
    fn handle(&self, _req: RequestData) -> crate::response::ResponseData {
        let mut resp =
            crate::response::ResponseData::with_body(self.response_body.as_bytes().to_vec());
        resp.set_header("Content-Type", &self.content_type);
        resp
    }
}

use pyo3::prelude::*;
use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, Ordering};

use crate::websocket::TurboWebSocketHandler;

/// Shared application state
pub struct AppState {
    pub routes: RwLock<Router>,
    pub debug: AtomicBool,
    pub websocket_handlers: RwLock<HashMap<String, Py<PyAny>>>,
    pub turbo_websocket_handlers: RwLock<HashMap<String, Arc<TurboWebSocketHandler>>>,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            routes: RwLock::new(Router::new()),
            debug: AtomicBool::new(false),
            websocket_handlers: RwLock::new(HashMap::new()),
            turbo_websocket_handlers: RwLock::new(HashMap::new()),
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
    mut payload: web::Payload,
    state: web::Data<Arc<AppState>>,
) -> HttpResponse {
    let start_time = Instant::now();

    // Check for WebSocket upgrade request
    let is_websocket = req
        .headers()
        .get("upgrade")
        .and_then(|v| v.to_str().ok())
        .map(|v| v.to_lowercase() == "websocket")
        .unwrap_or(false);

    if is_websocket {
        let path = req.path().to_string();

        // Check for Turbo WebSocket handlers first (pure Rust, maximum performance)
        {
            let turbo_handlers = state.turbo_websocket_handlers.read().await;
            if let Some(handler) = turbo_handlers.get(&path) {
                let handler_clone = handler.clone();
                drop(turbo_handlers);

                match crate::websocket::handle_turbo_websocket(req, payload, handler_clone).await {
                    Ok(response) => return response,
                    Err(e) => {
                        return HttpResponse::InternalServerError()
                            .body(format!("Turbo WebSocket error: {}", e));
                    }
                }
            }
        }

        // Fall back to Python WebSocket handlers
        let ws_handlers = state.websocket_handlers.read().await;

        if let Some(handler) = ws_handlers.get(&path) {
            let handler_clone = Python::attach(|py| handler.clone_ref(py));
            drop(ws_handlers);

            match crate::websocket::handle_websocket(req, payload, handler_clone).await {
                Ok(response) => return response,
                Err(e) => {
                    return HttpResponse::InternalServerError()
                        .body(format!("WebSocket error: {}", e));
                }
            }
        }
        // If no WS handler registered for this path, fall through to normal handling
        drop(ws_handlers);
    }

    // 1. Convert Actix Request to generic RequestData
    let mut headers = std::collections::HashMap::new();
    for (key, value) in req.headers() {
        if let Ok(v) = value.to_str() {
            headers.insert(key.to_string(), v.to_string());
        }
    }

    // Parse query params slightly redundantly but accurately
    let query_params = if !req.query_string().is_empty() {
        url::form_urlencoded::parse(req.query_string().as_bytes())
            .into_owned()
            .collect()
    } else {
        std::collections::HashMap::new()
    };

    // 2. Handle Body (Multipart or Regular)
    let mut files = std::collections::HashMap::new();
    let mut multipart_form = std::collections::HashMap::new();
    let mut body_bytes = Vec::new();

    let content_type = headers
        .get("content-type")
        .map(|ct| ct.to_lowercase())
        .unwrap_or_default();

    if content_type.contains("multipart/form-data") {
        let mut multipart = Multipart::new(req.headers(), payload);
        while let Ok(Some(mut field)) = multipart.try_next().await {
            // Note: In some versions content_disposition returns Option, compiler says it does.
            if let Some(content_disposition) = field.content_disposition() {
                let name = content_disposition.get_name().unwrap_or("").to_string();
                let filename = content_disposition.get_filename().map(|f| f.to_string());

                let mut field_bytes = Vec::new();
                while let Some(chunk) = field.next().await {
                    if let Ok(data) = chunk {
                        field_bytes.extend_from_slice(&data);
                    }
                }

                if let Some(fname) = filename {
                    files.insert(
                        name,
                        crate::request::UploadedFile {
                            filename: fname,
                            content_type: field
                                .content_type()
                                .map(|ct| ct.to_string())
                                .unwrap_or_default(),
                            content: field_bytes,
                        },
                    );
                } else if let Ok(s) = String::from_utf8(field_bytes) {
                    multipart_form.insert(name, s);
                }
            }
        }
    } else {
        // Regular body
        while let Some(chunk) = payload.next().await {
            if let Ok(data) = chunk {
                body_bytes.extend_from_slice(&data);
            }
        }
    }

    let request_data = RequestData {
        method: req.method().clone(),
        path: req.path().to_string(),
        query_string: req.query_string().to_string(),
        headers,
        body: body_bytes,
        query_params,
        files,
        multipart_form,
    };

    // 2. Dispatch to Router
    let routes = state.routes.read().await;
    let response_data = routes.process_request(request_data);
    drop(routes);

    // 3. Convert ResponseData to Actix Response

    // Check if it's a streaming response
    if let Some(iterator) = response_data.stream_iterator {
        let stream = crate::server::stream::PythonStream::new(iterator);
        let mut builder = HttpResponse::build(response_data.status);

        for (k, v) in response_data.headers {
            builder.insert_header((k.as_str(), v.as_str()));
        }

        if state.debug.load(Ordering::Relaxed) {
            crate::logger::log_request_optimized(
                req.method().as_ref(),
                req.path(),
                response_data.status.as_u16(),
                start_time.elapsed().as_secs_f64(),
                true,
            );
        }
        return builder.streaming(stream);
    }

    // Check if it's a file response
    if let Some(path_str) = response_data.file_path {
        let path = std::path::Path::new(&path_str);
        if path.exists() {
            let named_file = actix_files::NamedFile::open(path);
            match named_file {
                Ok(nf) => {
                    // NamedFile handles Range requests automatically!
                    // We can still apply custom headers
                    let mut response = nf.into_response(&req);

                    // Apply custom headers from ResponseData
                    for (k, v) in response_data.headers {
                        response.headers_mut().insert(
                            actix_web::http::header::HeaderName::from_bytes(k.as_bytes()).unwrap(),
                            actix_web::http::header::HeaderValue::from_str(&v).unwrap(),
                        );
                    }

                    if state.debug.load(Ordering::Relaxed) {
                        crate::logger::log_request_optimized(
                            req.method().as_ref(),
                            req.path(),
                            response.status().as_u16(),
                            start_time.elapsed().as_secs_f64(),
                            true,
                        );
                    }

                    return response;
                }
                Err(_) => {
                    if state.debug.load(Ordering::Relaxed) {
                        crate::logger::log_request_optimized(
                            req.method().as_ref(),
                            req.path(),
                            500,
                            start_time.elapsed().as_secs_f64(),
                            true,
                        );
                    }
                    return HttpResponse::InternalServerError().body("File Open Error");
                }
            }
        }
    }

    let mut builder = HttpResponse::build(response_data.status);

    for (k, v) in response_data.headers {
        builder.insert_header((k.as_str(), v.as_str()));
    }

    if state.debug.load(Ordering::Relaxed) {
        crate::logger::log_request_optimized(
            req.method().as_ref(),
            req.path(),
            response_data.status.as_u16(),
            start_time.elapsed().as_secs_f64(),
            true,
        );
    }

    builder.body(response_data.body)
}
