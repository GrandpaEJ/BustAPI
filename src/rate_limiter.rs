use dashmap::DashMap;
use pyo3::prelude::*;
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};

/// A high-performance rate limiter using DashMap for concurrent access
#[pyclass(name = "PyRateLimiter")]
#[derive(Clone)]
pub struct PyRateLimiter {
    // key -> (timestamp, count)
    // Simple fixed window for MVP
    // Or maybe list of timestamps?
    // Let's implement a sliding window log or simpler fixed window.
    // For "5/minute", fixed window is easiest to implement efficiently.
    // Key: "ip:route", Value: (window_start_timestamp, count)
    limits: Arc<DashMap<String, (u64, u32)>>,
}

#[pymethods]
impl PyRateLimiter {
    #[new]
    fn new() -> Self {
        PyRateLimiter {
            limits: Arc::new(DashMap::new()),
        }
    }

    /// Check if a request is allowed
    /// Returns true if allowed, false if blocked
    ///
    /// Args:
    ///     key: Unique key for the request (e.g. "ip:route")
    ///     limit: Max numbers of requests
    ///     period: Time window in seconds
    fn check_limit(&self, key: String, limit: u32, period: u64) -> bool {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        // DashMap entry API for atomic updates
        let mut entry = self.limits.entry(key).or_insert((now, 0));
        let (window_start, count) = entry.value_mut();

        if now >= *window_start + period {
            // New window
            *window_start = now;
            *count = 1;
            true
        } else {
            // Existing window
            if *count < limit {
                *count += 1;
                true
            } else {
                false
            }
        }
    }

    /// Clear all limits
    fn clear(&self) {
        self.limits.clear();
    }
}
