#[cfg(test)]
use super::handlers::*;

#[test]
fn test_router_creation() {
    let router = Router::new();
    assert_eq!(router.routes.len(), 0);
    assert_eq!(router.middleware.len(), 0);
}
