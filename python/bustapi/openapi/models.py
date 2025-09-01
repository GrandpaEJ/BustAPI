"""
BustAPI OpenAPI Models

Simplified OpenAPI 3.1.0 specification models for BustAPI.
Custom implementation optimized for BustAPI's needs.
"""

from typing import Any, Dict, List, Optional


class OpenAPIInfo:
    """API information for OpenAPI spec."""

    def __init__(self, title: str, version: str, description: Optional[str] = None):
        self.title = title
        self.version = version
        self.description = description


class OpenAPIServer:
    """Server information for OpenAPI spec."""

    def __init__(self, url: str, description: Optional[str] = None):
        self.url = url
        self.description = description


class OpenAPIResponse:
    """Response information for OpenAPI spec."""

    def __init__(self, description: str, content: Optional[Dict[str, Any]] = None):
        self.description = description
        self.content = content or {}


class OpenAPIOperation:
    """Operation information for OpenAPI spec."""

    def __init__(
        self,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        operation_id: Optional[str] = None,
        responses: Optional[Dict[str, OpenAPIResponse]] = None,
        tags: Optional[List[str]] = None,
    ):
        self.summary = summary
        self.description = description
        self.operationId = operation_id
        self.responses = responses or {"200": OpenAPIResponse("Successful response")}
        self.tags = tags or []


class OpenAPIPathItem:
    """Path item for OpenAPI spec."""

    def __init__(self):
        self.get: Optional[OpenAPIOperation] = None
        self.post: Optional[OpenAPIOperation] = None
        self.put: Optional[OpenAPIOperation] = None
        self.delete: Optional[OpenAPIOperation] = None
        self.patch: Optional[OpenAPIOperation] = None
        self.head: Optional[OpenAPIOperation] = None
        self.options: Optional[OpenAPIOperation] = None


class OpenAPISpec:
    """Complete OpenAPI specification."""

    def __init__(
        self,
        info: OpenAPIInfo,
        servers: Optional[List[OpenAPIServer]] = None,
        paths: Optional[Dict[str, OpenAPIPathItem]] = None,
    ):
        self.openapi = "3.1.0"
        self.info = info
        self.servers = servers or []
        self.paths = paths or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "openapi": self.openapi,
            "info": {
                "title": self.info.title,
                "version": self.info.version,
            },
            "paths": {},
        }

        if self.info.description:
            result["info"]["description"] = self.info.description

        if self.servers:
            result["servers"] = [
                {"url": server.url, "description": server.description}
                for server in self.servers
            ]

        for path, path_item in self.paths.items():
            path_dict = {}

            for method in ["get", "post", "put", "delete", "patch", "head", "options"]:
                operation = getattr(path_item, method, None)
                if operation:
                    op_dict = {
                        "responses": {
                            code: {"description": resp.description}
                            for code, resp in operation.responses.items()
                        }
                    }

                    if operation.summary:
                        op_dict["summary"] = operation.summary
                    if operation.description:
                        op_dict["description"] = operation.description
                    if operation.operationId:
                        op_dict["operationId"] = operation.operationId
                    if operation.tags:
                        op_dict["tags"] = operation.tags

                    path_dict[method] = op_dict

            if path_dict:
                result["paths"][path] = path_dict

        return result
