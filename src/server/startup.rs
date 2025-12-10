//! Server startup and configuration

use super::handlers::{AppState, ServerConfig};
use actix_web::{web, App, HttpServer};
use std::sync::Arc;

/// Start the Actix-web server
pub async fn start_server(config: ServerConfig, state: Arc<AppState>) -> std::io::Result<()> {
    let addr = format!("{}:{}", config.host, config.port);

    let pid = std::process::id();
    let route_count = state.routes.read().await.route_count();
    let workers = config.workers;

    // Stylish Banner (Fiber-like)
    use colored::Colorize;

    println!("┌───────────────────────────────────────────────────┐");
    println!(
        "│                   {}                  │",
        "BustAPI v0.2.2".cyan().bold()
    );
    println!("│               http://{:<21}│", addr);
    println!(
        "│       (bound on host {} and port {})       │",
        config.host, config.port
    );
    println!("│                                                   │");
    println!(
        "│ Handlers ............. {:<3} Processes ........... {:<2} │",
        route_count, workers
    );
    println!("│ Prefork ....... Disabled  PID ............. {:<5} │", pid);
    println!("└───────────────────────────────────────────────────┘");

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
