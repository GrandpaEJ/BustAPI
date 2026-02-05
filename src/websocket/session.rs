//! WebSocket session handling
//!
//! Manages individual WebSocket connections with message routing.

use actix_web::{web, HttpRequest, HttpResponse};
use actix_ws::Message;
use futures::StreamExt;
use pyo3::prelude::*;
use std::sync::Arc;
use tokio::sync::mpsc;

/// Message types for WebSocket communication
#[derive(Debug, Clone)]
pub enum WebSocketMessage {
    Text(String),
    Binary(Vec<u8>),
    Ping(Vec<u8>),
    Pong(Vec<u8>),
    Close(Option<String>),
}

/// WebSocket session state
pub struct WebSocketSession {
    /// Unique session ID
    pub id: u64,
    /// Channel for sending messages to the client
    tx: mpsc::UnboundedSender<WebSocketMessage>,
}

impl WebSocketSession {
    /// Create a new WebSocket session
    pub fn new(id: u64, tx: mpsc::UnboundedSender<WebSocketMessage>) -> Self {
        Self { id, tx }
    }

    /// Send a text message to the client
    /// Send a text message to the client
    pub async fn send_text(
        &self,
        text: String,
    ) -> Result<(), mpsc::error::SendError<WebSocketMessage>> {
        self.tx.send(WebSocketMessage::Text(text))
    }

    /// Send binary data to the client
    pub async fn send_binary(
        &self,
        data: Vec<u8>,
    ) -> Result<(), mpsc::error::SendError<WebSocketMessage>> {
        self.tx.send(WebSocketMessage::Binary(data))
    }

    /// Close the connection
    pub async fn close(
        &self,
        reason: Option<String>,
    ) -> Result<(), mpsc::error::SendError<WebSocketMessage>> {
        self.tx.send(WebSocketMessage::Close(reason))
    }
}

/// Counter for generating unique session IDs
static SESSION_COUNTER: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);

use crate::websocket::WebSocketConfig;

use std::collections::HashMap;

/// Handle WebSocket upgrade and message loop
pub async fn handle_websocket(
    req: HttpRequest,
    payload: web::Payload,
    handler: Py<PyAny>,
    config: Option<WebSocketConfig>,
    headers: HashMap<String, String>,
    cookies: HashMap<String, String>,
) -> Result<HttpResponse, actix_web::Error> {
    // Upgrade the connection
    let (response, mut session, mut msg_stream) = actix_ws::handle(&req, payload)?;

    // Generate unique session ID
    let session_id = SESSION_COUNTER.fetch_add(1, std::sync::atomic::Ordering::Relaxed);

    // Create channel for outgoing messages (Unbounded)
    let (tx, mut rx) = mpsc::unbounded_channel::<WebSocketMessage>();

    // Create session wrapper
    let ws_session = Arc::new(WebSocketSession::new(session_id, tx.clone()));

    // Spawn task for sending messages using spawn_local
    let mut session_clone = session.clone();
    tokio::task::spawn_local(async move {
        while let Some(msg) = rx.recv().await {
            match msg {
                WebSocketMessage::Text(text) => {
                    let _ = session_clone.text(text).await;
                }
                WebSocketMessage::Binary(data) => {
                    let _ = session_clone.binary(data).await;
                }
                WebSocketMessage::Ping(data) => {
                    let _ = session_clone.ping(&data).await;
                }
                WebSocketMessage::Pong(data) => {
                    let _ = session_clone.pong(&data).await;
                }
                WebSocketMessage::Close(reason) => {
                    let _ = session_clone
                        .close(reason.map(|r| actix_ws::CloseReason {
                            code: actix_ws::CloseCode::Normal,
                            description: Some(r),
                        }))
                        .await;
                    break;
                }
            }
        }
    });

    // Clone handler for use in async context
    let handler_for_connect = Python::attach(|py| handler.clone_ref(py));
    let tx_for_python = tx.clone();

    // Call Python on_connect handler
    Python::attach(move |py| {
        println!(
            "DEBUG: Calling Python on_connect for session {}",
            session_id
        );
        let py_conn =
            crate::bindings::websocket::PyWebSocketConnection::new(session_id, tx_for_python);
        let res = handler_for_connect.call_method1(py, "on_connect", (py_conn, headers, cookies));
        if let Err(e) = res {
            println!("DEBUG: Python on_connect FAILED: {}", e);
            e.print_and_set_sys_last_vars(py);
        } else {
            println!(
                "DEBUG: Python on_connect success for session {}",
                session_id
            );
        }
    });

    // Clone handler for message loop
    let handler_for_messages = Python::attach(|py| handler.clone_ref(py));

    // Spawn task for receiving messages
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
                    let text_str = text.to_string();
                    let sid = ws_session.id;
                    let tx_clone = ws_session.tx.clone();
                    let handler_ref = Python::attach(|py| handler_for_messages.clone_ref(py));

                    // Call Python on_message handler
                    Python::attach(|py| {
                        // Get response from Python handler
                        if let Ok(result) =
                            handler_ref.call_method1(py, "on_message", (sid, text_str))
                        {
                            // If handler returns a string, send it back
                            if let Ok(response) = result.extract::<String>(py) {
                                let tx = tx_clone.clone();
                                actix_rt::spawn(async move {
                                    let _ = tx.send(WebSocketMessage::Text(response));
                                });
                            }
                        }
                    });
                }
                Message::Binary(data) => {
                    let data_vec = data.to_vec();
                    let sid = ws_session.id;
                    let handler_ref = Python::attach(|py| handler_for_messages.clone_ref(py));

                    Python::attach(|py| {
                        let _ = handler_ref.call_method1(py, "on_binary", (sid, data_vec));
                    });
                }
                Message::Ping(data) => {
                    let _ = session.pong(&data).await;
                }
                Message::Pong(_) => {
                    // Pong received, connection is alive
                }
                Message::Close(reason) => {
                    let sid = ws_session.id;
                    let reason_str = reason.map(|r| r.description.unwrap_or_default());
                    let handler_ref = Python::attach(|py| handler_for_messages.clone_ref(py));

                    Python::attach(|py| {
                        let _ = handler_ref.call_method1(py, "on_disconnect", (sid, reason_str));
                    });
                    break;
                }
                _ => {
                    // Continuation frames handled internally by actix-ws
                }
            }
        }
    });

    Ok(response)
}
