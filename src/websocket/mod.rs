//! WebSocket support for BustAPI
//!
//! This module provides high-performance WebSocket handling using actix-ws.

mod session;
mod turbo;

pub use session::{handle_websocket, WebSocketMessage, WebSocketSession};
pub use turbo::{handle_turbo_websocket, TurboWebSocketHandler};
