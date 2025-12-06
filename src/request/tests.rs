#[cfg(test)]
use crate::request::methods::*;
#[allow(unused_imports)]
use http::Method;

#[test]
fn test_request_creation() {
    let req = RequestData::new(Method::GET, "/test".to_string());
    assert_eq!(req.method, Method::GET);
    assert_eq!(req.path, "/test");
    assert!(req.headers.is_empty());
    assert!(req.body.is_empty());
}

#[test]
fn test_header_retrieval() {
    let mut req = RequestData::new(Method::GET, "/".to_string());
    req.headers
        .insert("Content-Type".to_string(), "application/json".to_string());

    assert_eq!(
        req.get_header("content-type"),
        Some(&"application/json".to_string())
    );
    assert_eq!(
        req.get_header("Content-Type"),
        Some(&"application/json".to_string())
    );
    assert_eq!(req.get_header("missing"), None);
}

#[test]
fn test_json_detection() {
    let mut req = RequestData::new(Method::POST, "/".to_string());
    req.headers
        .insert("Content-Type".to_string(), "application/json".to_string());

    assert!(req.is_json());
    assert!(!req.is_form());
}

#[test]
fn test_cookie_parsing() {
    let mut req = RequestData::new(Method::GET, "/".to_string());
    req.headers.insert(
        "Cookie".to_string(),
        "session=abc123; theme=dark".to_string(),
    );

    let cookies = req.get_cookies();
    assert_eq!(cookies.get("session"), Some(&"abc123".to_string()));
    assert_eq!(cookies.get("theme"), Some(&"dark".to_string()));
}
