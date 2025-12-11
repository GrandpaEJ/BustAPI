//! Actix-web HTTP Server implementation for maximum performance

use actix_multipart::Multipart;
use actix_web::{web, HttpRequest, HttpResponse};
use futures::{StreamExt, TryStreamExt};
use std::sync::Arc;
use tokio::sync::RwLock;

use crate::request::RequestData;
use crate::router::{RouteHandler, Router};

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

/// Shared application state
pub struct AppState {
    pub routes: RwLock<Router>,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            routes: RwLock::new(Router::new()),
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
    let mut builder = HttpResponse::build(response_data.status);

    for (k, v) in response_data.headers {
        builder.insert_header((k.as_str(), v.as_str()));
    }

    builder.body(response_data.body)
}
