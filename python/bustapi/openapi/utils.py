"""
BustAPI OpenAPI Utils

Utilities for generating OpenAPI specifications for BustAPI applications.
"""

from typing import Any, Dict, List, Optional

from .models import (
    OpenAPIInfo,
    OpenAPIOperation,
    OpenAPIPathItem,
    OpenAPIResponse,
    OpenAPIServer,
    OpenAPISpec,
)


def get_openapi_spec(
    title: str,
    version: str,
    description: Optional[str] = None,
    routes: Optional[List[Any]] = None,
    servers: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Generate OpenAPI specification for BustAPI application.

    Args:
        title: API title
        version: API version
        description: API description
        routes: List of routes to document
        servers: List of server configurations

    Returns:
        OpenAPI specification as dictionary
    """
    # Create info object
    info = OpenAPIInfo(title=title, version=version, description=description)

    # Create servers
    server_objects = []
    if servers:
        for server in servers:
            server_objects.append(
                OpenAPIServer(
                    url=server.get("url", "/"), description=server.get("description")
                )
            )

    # Create paths from routes
    paths = {}
    if routes:
        for route in routes:
            path_item = create_path_item_from_route(route)
            if path_item:
                paths[route.get("path", "/")] = path_item

    # Create OpenAPI spec
    spec = OpenAPISpec(info=info, servers=server_objects, paths=paths)

    return spec.to_dict()


def create_path_item_from_route(route: Dict[str, Any]) -> Optional[OpenAPIPathItem]:
    """
    Create OpenAPI path item from route information.

    Args:
        route: Route information dictionary

    Returns:
        OpenAPI path item or None
    """
    if not route:
        return None

    path_item = OpenAPIPathItem()
    methods = route.get("methods", ["GET"])
    handler = route.get("handler")

    for method in methods:
        method_lower = method.lower()
        if hasattr(path_item, method_lower):
            operation = create_operation_from_handler(handler, method)
            setattr(path_item, method_lower, operation)

    return path_item


def create_operation_from_handler(handler: Any, method: str) -> OpenAPIOperation:
    """
    Create OpenAPI operation from route handler.

    Args:
        handler: Route handler function
        method: HTTP method

    Returns:
        OpenAPI operation
    """
    if not handler:
        return OpenAPIOperation()

    # Extract information from handler
    summary = None
    description = None
    operation_id = None

    if hasattr(handler, "__name__"):
        operation_id = f"{method.lower()}_{handler.__name__}"

    if hasattr(handler, "__doc__") and handler.__doc__:
        doc_lines = handler.__doc__.strip().split("\n")
        if doc_lines:
            summary = doc_lines[0].strip()
            if len(doc_lines) > 1:
                description = "\n".join(line.strip() for line in doc_lines[1:]).strip()

    # Create default responses
    responses = {
        "200": OpenAPIResponse("Successful response"),
        "422": OpenAPIResponse("Validation Error"),
    }

    return OpenAPIOperation(
        summary=summary,
        description=description,
        operation_id=operation_id,
        responses=responses,
    )


def extract_route_info(app) -> List[Dict[str, Any]]:
    """
    Extract route information from BustAPI application.

    Args:
        app: BustAPI application instance

    Returns:
        List of route information dictionaries
    """
    routes = []

    # Try to get routes from the app
    if hasattr(app, "_routes"):
        for path, route_info in app._routes.items():
            routes.append(
                {
                    "path": path,
                    "methods": route_info.get("methods", ["GET"]),
                    "handler": route_info.get("handler"),
                }
            )

    return routes
