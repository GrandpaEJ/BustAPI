"""
Optional documentation support for BustAPI.

This module provides the BustAPIDocs extension, which adds OpenAPI (Swagger)
and ReDoc documentation to a BustAPI application.
"""

import inspect
import json
from typing import Any, Dict, List, Optional

from .app import BustAPI
from .response import Response


class BustAPIDocs:
    """
    Extension for adding OpenAPI documentation to BustAPI.

    Usage:
        app = BustAPI()
        docs = BustAPIDocs(app, title="My API")
    """

    def __init__(
        self,
        app: Optional[BustAPI] = None,
        title: str = "BustAPI",
        version: str = "0.1.0",
        description: str = "",
        docs_url: Optional[str] = "/docs",
        redoc_url: Optional[str] = "/redoc",
        openapi_url: Optional[str] = "/openapi.json",
    ):
        self.title = title
        self.version = version
        self.description = description
        self.docs_url = docs_url
        self.redoc_url = redoc_url
        self.openapi_url = openapi_url
        self._schema_cache: Optional[Dict[str, Any]] = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: BustAPI):
        """Initialize the extension with the application."""
        self.app = app

        if self.openapi_url:
            app.add_url_rule(
                self.openapi_url, "openapi_schema", self._openapi_route, methods=["GET"]
            )

        if self.docs_url and self.openapi_url:
            app.add_url_rule(
                self.docs_url, "swagger_ui", self._swagger_ui_route, methods=["GET"]
            )

        if self.redoc_url and self.openapi_url:
            app.add_url_rule(
                self.redoc_url, "redoc_ui", self._redoc_ui_route, methods=["GET"]
            )

    def _openapi_route(self) -> Response:
        """Route handler for OpenAPI JSON schema."""
        schema = self.get_openapi_schema()
        return Response(json.dumps(schema), mimetype="application/json")

    def _swagger_ui_route(self) -> Response:
        """Route handler for Swagger UI."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
        <title>{self.title} - Swagger UI</title>
        </head>
        <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
        const ui = SwaggerUIBundle({{
            url: '{self.openapi_url}',
            dom_id: '#swagger-ui',
            presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout",
            deepLinking: true,
            showExtensions: true,
            showCommonExtensions: true
        }})
        </script>
        </body>
        </html>
        """
        return Response(html, mimetype="text/html")

    def _redoc_ui_route(self) -> Response:
        """Route handler for ReDoc UI."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>{self.title} - ReDoc</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body {{
            margin: 0;
            padding: 0;
            }}
        </style>
        </head>
        <body>
        <redoc spec-url='{self.openapi_url}'></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"> </script>
        </body>
        </html>
        """
        return Response(html, mimetype="text/html")

    def get_openapi_schema(self) -> Dict[str, Any]:
        """Generate or return cached OpenAPI schema."""
        if self._schema_cache:
            return self._schema_cache

        schema = {
            "openapi": "3.0.2",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": self.description,
            },
            "paths": {},
            "components": {"schemas": {}},
        }

        # Inspect routes
        for rule, endpoint_info in self.app.url_map.items():
            endpoint_name = endpoint_info["endpoint"]
            methods = endpoint_info["methods"]

            # Skip internal routes
            if endpoint_name in ["openapi_schema", "swagger_ui", "redoc_ui", "static"]:
                continue

            # Get handler function
            view_func = self.app.view_functions.get(endpoint_name)
            if not view_func:
                continue

            path_item = {}
            
            # Convert Flask rule to OpenAPI path
            # e.g., /user/<name> -> /user/{name}
            openapi_path = rule.replace("<", "{").replace(">", "}")

            docstring = inspect.getdoc(view_func) or ""
            summary = docstring.split("\n")[0] if docstring else endpoint_name
            description = docstring

            for method in methods:
                method_lower = method.lower()
                if method_lower not in ["get", "post", "put", "delete", "patch", "options", "head"]:
                    continue

                operation = {
                    "summary": summary,
                    "description": description,
                    "operationId": f"{endpoint_name}_{method_lower}",
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                        }
                    },
                }
                
                # Basic parameter extraction from rule
                # This is a simplified implementation. A full one would parse the rule
                # and type hints to generate detailed parameters.
                if "{" in openapi_path:
                    parameters = []
                    # Extract param names from rule (simplified)
                    import re
                    param_names = re.findall(r"\{([^}]+)\}", openapi_path)
                    for name in param_names:
                        parameters.append({
                            "name": name,
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        })
                    operation["parameters"] = parameters

                path_item[method_lower] = operation

            if path_item:
                schema["paths"][openapi_path] = path_item

        self._schema_cache = schema
        return schema
