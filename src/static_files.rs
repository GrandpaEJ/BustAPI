use crate::request::RequestData;
use crate::response::ResponseData;
use crate::router::RouteHandler;
use http::StatusCode;
use std::fs;
use std::path::{Path, PathBuf};

/// Secure implementation of static file serving
pub struct StaticFileHandler {
    root_path: PathBuf,
    path_prefix: String,
}

impl StaticFileHandler {
    /// Create a new static file handler
    pub fn new(root_path: &str, path_prefix: &str) -> Self {
        // Resolve path relative to current working directory if it's relative
        let path = Path::new(root_path);
        let absolute_root = if path.is_absolute() {
            path.to_path_buf()
        } else {
            std::env::current_dir()
                .unwrap_or_else(|_| PathBuf::from("."))
                .join(path)
        };

        // Try to canonicalize to resolve symlinks/.. but tolerate failure (e.g. if dir doesn't exist yet)
        let resolved_root = fs::canonicalize(&absolute_root).unwrap_or(absolute_root);

        Self {
            root_path: resolved_root,
            path_prefix: path_prefix.to_string(),
        }
    }

    /// Sanitize path and check for security violations
    /// Returns: Option<PathBuf> if safe and valid, None if unsafe/blocked
    fn resolve_safe_path(&self, req_path: &str) -> Option<PathBuf> {
        // 1. Strip prefix
        if !req_path.starts_with(&self.path_prefix) {
            return None;
        }

        // Remove prefix to get relative path
        let relative_path = &req_path[self.path_prefix.len()..];
        let relative_path = relative_path.trim_start_matches('/');

        // 2. Security Check: Prevent Path Traversal ".."
        // Rust's Path components iteration handles some of this, but we need to be explicit.
        if relative_path.contains("..") {
            tracing::warn!("Blocked path traversal attempt: {}", req_path);
            return None;
        }

        // 3. Security Check: Block Hidden/Sensitive Files
        // Reject any segment starting with '.' (e.g., .env, .git, .vscode)
        for component in Path::new(relative_path).components() {
            if let Some(s) = component.as_os_str().to_str() {
                if s.starts_with('.') {
                    tracing::warn!("Blocked access to sensitive file: {}", req_path);
                    return None;
                }
            }
        }

        // 4. Resolve full path
        let full_path = self.root_path.join(relative_path);

        // 5. Final Security Check: Ensure resolved path is still within root
        // This handles symlink attacks if fs::canonicalize was used effectively
        if !full_path.starts_with(&self.root_path) {
            return None;
        }

        Some(full_path)
    }
}

impl RouteHandler for StaticFileHandler {
    fn handle(&self, req: RequestData) -> ResponseData {
        if req.method != http::Method::GET && req.method != http::Method::HEAD {
            return ResponseData::error(StatusCode::METHOD_NOT_ALLOWED, Some("Method Not Allowed"));
        }

        if let Some(path) = self.resolve_safe_path(&req.path) {
            if path.exists() && path.is_file() {
                // Use shared logic for file serving with Range support (handled by server/handlers.rs)
                let mut resp = ResponseData::new();
                resp.file_path = Some(path.to_string_lossy().to_string());
                return resp;
            }
        }

        // Generic 404 for any failure (file not found, security block, directory access)
        ResponseData::error(StatusCode::NOT_FOUND, Some("Not Found"))
    }
}
