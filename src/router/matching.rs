//! Route pattern matching for dynamic routes

use crate::request::RequestData;
use crate::router::handlers::RouteHandler;
use http::Method;
use std::collections::HashMap;
use std::sync::Arc;

/// Find pattern match for dynamic routes like /greet/<name> or /users/<int:id>
pub fn find_pattern_match(
    routes: &HashMap<(Method, String), Arc<dyn RouteHandler>>,
    req: &RequestData,
) -> Option<Arc<dyn RouteHandler>> {
    // Normalize path segments
    let req_parts: Vec<&str> = req.path.trim_matches('/').split('/').collect();

    for ((method, pattern), handler) in routes.iter() {
        if method != req.method {
            continue;
        }

        // Skip non-pattern routes here (they are handled by exact match earlier)
        if !pattern.contains('<') || !pattern.contains('>') {
            continue;
        }

        let pat_parts: Vec<&str> = pattern.trim_matches('/').split('/').collect();
        if pat_parts.len() != req_parts.len() {
            continue;
        }

        let mut matched = true;

        for (pp, rp) in pat_parts.iter().zip(req_parts.iter()) {
            if pp.starts_with('<') && pp.ends_with('>') {
                // Pattern segment, optionally typed like <int:id> or just <name>
                let inner = &pp[1..pp.len() - 1];
                let (typ, _name) = if let Some((t, n)) = inner.split_once(':') {
                    (t.trim(), n.trim())
                } else {
                    ("str", inner.trim())
                };

                // Minimal type checks
                match typ {
                    "int" => {
                        if rp.parse::<i64>().is_err() {
                            matched = false;
                            break;
                        }
                    }
                    // Accept any non-empty string for str/float/path/etc. for now
                    _ => {
                        if rp.is_empty() {
                            matched = false;
                            break;
                        }
                    }
                }
            } else if pp != rp {
                matched = false;
                break;
            }
        }

        if matched {
            return Some(handler.clone());
        }
    }

    None
}
