//! Server startup and configuration

use super::handlers::{AppState, ServerConfig};
use actix_web::{web, App, HttpServer};
use std::sync::Arc;

/// Start the Actix-web server
pub async fn start_server(config: ServerConfig, state: Arc<AppState>) -> std::io::Result<()> {
    let addr = format!("{}:{}", config.host, config.port);

    tracing::info!("🚀 BustAPI server starting on http://{}", addr);
    tracing::info!("   Workers: {}", config.workers);

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(state.clone()))
            .default_service(web::route().to(super::handlers::handle_request))
    })
    .workers(config.workers)
    .bind(&addr)?
    .run()
    .await
}
