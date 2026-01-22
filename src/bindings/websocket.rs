//! Python bindings for WebSocket support
//!
//! Exposes WebSocket functionality to Python.

use pyo3::prelude::*;
use tokio::sync::mpsc;

use crate::websocket::WebSocketMessage;

/// Python-accessible WebSocket session wrapper
#[pyclass(name = "WebSocketConnection")]
#[derive(Clone)]
pub struct PyWebSocketConnection {
    /// Session ID
    #[pyo3(get)]
    pub id: u64,
    /// Message sender channel
    tx: mpsc::Sender<WebSocketMessage>,
}

#[pymethods]
impl PyWebSocketConnection {
    /// Send a text message to the client
    fn send(&self, message: String) -> PyResult<()> {
        let tx = self.tx.clone();
        // Use blocking send for simplicity in sync Python context
        pyo3_async_runtimes::tokio::get_runtime().block_on(async {
            tx.send(WebSocketMessage::Text(message)).await.map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Send error: {}", e))
            })
        })
    }

    /// Send binary data to the client
    fn send_binary(&self, data: Vec<u8>) -> PyResult<()> {
        let tx = self.tx.clone();
        pyo3_async_runtimes::tokio::get_runtime().block_on(async {
            tx.send(WebSocketMessage::Binary(data)).await.map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Send error: {}", e))
            })
        })
    }

    /// Close the connection
    fn close(&self, reason: Option<String>) -> PyResult<()> {
        let tx = self.tx.clone();
        pyo3_async_runtimes::tokio::get_runtime().block_on(async {
            tx.send(WebSocketMessage::Close(reason)).await.map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Close error: {}", e))
            })
        })
    }
}

impl PyWebSocketConnection {
    /// Create a new Python WebSocket connection wrapper
    pub fn new(id: u64, tx: mpsc::Sender<WebSocketMessage>) -> Self {
        Self { id, tx }
    }
}

/// Python callable WebSocket handler wrapper
#[pyclass(name = "WebSocketHandler")]
pub struct PyWebSocketHandler {
    /// Python handler callback
    handler: Py<PyAny>,
}

#[pymethods]
impl PyWebSocketHandler {
    #[new]
    fn new(handler: Py<PyAny>) -> Self {
        Self { handler }
    }

    /// Called when a client connects
    fn on_connect(&self, session_id: u64) -> PyResult<()> {
        Python::attach(|py| {
            if let Ok(on_connect) = self.handler.getattr(py, "on_connect") {
                let _ = on_connect.call1(py, (session_id,));
            }
            Ok(())
        })
    }

    /// Called when a text message is received
    fn on_message(&self, session_id: u64, message: String) -> PyResult<Option<String>> {
        Python::attach(|py| {
            if let Ok(on_message) = self.handler.getattr(py, "on_message") {
                if let Ok(result) = on_message.call1(py, (session_id, message)) {
                    if let Ok(response) = result.extract::<String>(py) {
                        return Ok(Some(response));
                    }
                }
            }
            Ok(None)
        })
    }

    /// Called when binary data is received
    fn on_binary(&self, session_id: u64, data: Vec<u8>) -> PyResult<()> {
        Python::attach(|py| {
            if let Ok(on_binary) = self.handler.getattr(py, "on_binary") {
                let _ = on_binary.call1(py, (session_id, data));
            }
            Ok(())
        })
    }

    /// Called when a client disconnects
    fn on_disconnect(&self, session_id: u64, reason: Option<String>) -> PyResult<()> {
        Python::attach(|py| {
            if let Ok(on_disconnect) = self.handler.getattr(py, "on_disconnect") {
                let _ = on_disconnect.call1(py, (session_id, reason));
            }
            Ok(())
        })
    }
}
