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

    let mut best_match: Option<Arc<dyn RouteHandler>> = None;
    let mut best_score = -1;

    for ((method, pattern), handler) in routes.iter() {
        if method != req.method {
            continue;
        }

        // Skip non-pattern routes here (they are handled by exact match earlier)
        if !pattern.contains('<') || !pattern.contains('>') {
            continue;
        }

        let pat_parts: Vec<&str> = pattern.trim_matches('/').split('/').collect();

        // Check availability of "path" wildcard which allows matching multiple segments
        let is_path_wildcard = if let Some(last) = pat_parts.last() {
            last.starts_with("<path:") && last.ends_with('>')
        } else {
            false
        };

        if is_path_wildcard {
            // For wildcard, request must have at least as many parts as pattern
            if req_parts.len() < pat_parts.len() {
                continue;
            }
        } else if pat_parts.len() != req_parts.len() {
            continue;
        }

        let mut matched = true;
        let mut current_score = 0;

        for (i, pp) in pat_parts.iter().enumerate() {
            // For path wildcard, the request might be longer, but we only iterate pattern parts
            let rp = req_parts[i];

            if pp.starts_with('<') && pp.ends_with('>') {
                // Pattern segment, optionally typed like <int:id> or <path:p>
                let inner = &pp[1..pp.len() - 1];
                let (typ, _name) = if let Some((t, n)) = inner.split_once(':') {
                    (t.trim(), n.trim())
                } else {
                    ("str", inner.trim())
                };

                // Minimal type checks
                match typ {
                    "path" => {
                        // Path wildcard matches everything remaining
                        // Lowest priority for wildcard
                        current_score += 1;
                        matched = true;
                        break;
                    }
                    "int" => {
                        if rp.parse::<i64>().is_err() {
                            matched = false;
                            break;
                        }
                        // High priority for specific type
                        current_score += 5;
                    }
                    "float" => {
                        if rp.parse::<f64>().is_err() {
                            matched = false;
                            break;
                        }
                        current_score += 5;
                    }
                    // Accept any non-empty string for str/etc.
                    _ => {
                        if rp.is_empty() {
                            matched = false;
                            break;
                        }
                        // Medium priority for generic string
                        current_score += 2;
                    }
                }
            } else if *pp != rp {
                matched = false;
                break;
            } else {
                // Exact string match gets highest priority
                current_score += 10;
            }
        }

        if matched {
            // If we found a better match, update it
            if current_score > best_score {
                best_score = current_score;
                best_match = Some(handler.clone());
            }
        }
    }

    best_match
}
