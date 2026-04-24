//! Turbo WebSocket - Pure Rust message handling for maximum performance
//!
//! This module provides a high-performance WebSocket handler that processes
//! messages entirely in Rust, calling Python only once during registration.

use actix_web::{web, HttpRequest, HttpResponse};
use actix_ws::Message;
use futures::StreamExt;
use std::sync::Arc;

/// Turbo WebSocket handler - processes messages in pure Rust
pub struct TurboWebSocketHandler {
    /// The response template - message will be formatted into this
    /// Format: "Echo: {}" where {} is replaced with the message
    response_prefix: String,
}

impl TurboWebSocketHandler {
    /// Create a new turbo handler with a response prefix
    pub fn new(response_prefix: String) -> Self {
        Self { response_prefix }
    }

    /// Format response for a message
    #[inline]
    pub fn format_response(&self, message: &str) -> String {
        format!("{}{}", self.response_prefix, message)
    }
}

use crate::websocket::WebSocketConfig;

/// Handle Turbo WebSocket - pure Rust, no Python per-message callbacks
pub async fn handle_turbo_websocket(
    req: HttpRequest,
    body: web::Payload,
    handler: Arc<TurboWebSocketHandler>,
    config: Option<WebSocketConfig>,
) -> Result<HttpResponse, actix_web::Error> {
    // Upgrade the connection
    let (response, mut session, mut msg_stream) = actix_ws::handle(&req, body)?;

    // Clone for the message loop
    let handler = handler.clone();

    // Spawn the message handling task
    actix_rt::spawn(async move {
        let mut last_tick = std::time::Instant::now();
        let mut msg_count = 0;

        while let Some(Ok(msg)) = msg_stream.next().await {
            // Apply Rate Limit
            if let Some(limit) = config.as_ref().and_then(|c| c.rate_limit) {
                if last_tick.elapsed().as_secs() >= 1 {
                    last_tick = std::time::Instant::now();
                    msg_count = 0;
                }
                msg_count += 1;
                if msg_count > limit {
                    let _ = session
                        .close(Some(actix_ws::CloseReason {
                            code: actix_ws::CloseCode::Policy,
                            description: Some("Rate limit exceeded".to_string()),
                        }))
                        .await;
                    break;
                }
            }

            match msg {
                Message::Text(text) => {
                    // Apply Size Limit
                    if let Some(limit) = config.as_ref().and_then(|c| c.max_message_size) {
                        if text.len() > limit {
                            let _ = session
                                .close(Some(actix_ws::CloseReason {
                                    code: actix_ws::CloseCode::Size,
                                    description: Some("Message too big".to_string()),
                                }))
                                .await;
                            break;
                        }
                    }
                    // Pure Rust message handling - no Python, no GIL
                    let response_text = handler.format_response(&text);
                    let _ = session.text(response_text).await;
                }
                Message::Binary(data) => {
                    // Echo binary data directly
                    let _ = session.binary(data).await;
                }
                Message::Ping(data) => {
                    let _ = session.pong(&data).await;
                }
                Message::Pong(_) => {
                    // Connection alive
                }
                Message::Close(reason) => {
                    let _ = session.close(reason).await;
                    break;
                }
                _ => {}
            }
        }
    });

    Ok(response)
}
