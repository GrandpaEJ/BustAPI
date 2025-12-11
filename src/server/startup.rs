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

    let version = env!("CARGO_PKG_VERSION");
    let banner_text = format!("BustAPI v{}", version);

    // Prepare all lines
    let line1 = banner_text.clone();
    let line2 = format!("http://{}", addr);
    let line3 = format!("(bound on host {} and port {})", config.host, config.port);
    let line4 = String::new(); // Empty line
    let line5 = format!(
        "Handlers ............. {}   Processes ........... {}",
        route_count, workers
    );
    let line6 = format!(
        "Debug ............ {}  PID ............. {}",
        config.debug, pid
    );

    // Find the longest line (without ANSI codes)
    let max_width = [
        line1.len(),
        line2.len(),
        line3.len(),
        line5.len(),
        line6.len(),
    ]
    .iter()
    .max()
    .unwrap_or(&0)
        + 4; // +4 for padding (2 on each side)

    let horizontal_line = "─".repeat(max_width);

    // Helper function to center text in box
    let center_in_box = |text: &str, width: usize| {
        let text_len = text.len();
        let total_padding = width.saturating_sub(text_len);
        let pad_left = total_padding / 2;
        let pad_right = total_padding - pad_left;
        format!(
            "│{}{}{}│",
            " ".repeat(pad_left),
            text,
            " ".repeat(pad_right)
        )
    };

    // Print the box
    println!("┌{}┐", horizontal_line);
    // For line1, calculate padding based on uncolored text, then apply color
    let line1_len = line1.len();
    let total_padding = max_width.saturating_sub(line1_len);
    let pad_left = total_padding / 2;
    let pad_right = total_padding - pad_left;
    println!(
        "│{}{}{}│",
        " ".repeat(pad_left),
        line1.cyan().bold(),
        " ".repeat(pad_right)
    );
    println!("{}", center_in_box(&line2, max_width));
    println!("{}", center_in_box(&line3, max_width));
    println!("{}", center_in_box(&line4, max_width));
    println!("{}", center_in_box(&line5, max_width));
    println!("{}", center_in_box(&line6, max_width));
    println!("└{}┘", horizontal_line);

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
