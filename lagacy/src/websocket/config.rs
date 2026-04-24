use pyo3::prelude::*;

/// Configuration for WebSocket routes
#[pyclass]
#[derive(Clone, Debug, Default)]
pub struct WebSocketConfig {
    /// Maximum message size in bytes (RAM limit)
    #[pyo3(get, set)]
    pub max_message_size: Option<usize>,

    /// Maximum messages per second per connection (CPU/Rate limit)
    #[pyo3(get, set)]
    pub rate_limit: Option<u64>,

    /// Heartbeat interval in seconds
    #[pyo3(get, set)]
    pub heartbeat_interval: Option<u64>,

    /// Client timeout in seconds
    #[pyo3(get, set)]
    pub timeout: Option<u64>,
}

#[pymethods]
impl WebSocketConfig {
    #[new]
    #[pyo3(signature = (max_message_size=None, rate_limit=None, heartbeat_interval=None, timeout=None))]
    pub fn new(
        max_message_size: Option<usize>,
        rate_limit: Option<u64>,
        heartbeat_interval: Option<u64>,
        timeout: Option<u64>,
    ) -> Self {
        Self {
            max_message_size,
            rate_limit,
            heartbeat_interval,
            timeout,
        }
    }
}
