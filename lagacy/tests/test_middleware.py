import pytest
from bustapi import BustAPI, Middleware, Response


class HeaderMiddleware(Middleware):
    def process_response(self, request, response):
        pass
        response.headers["X-Middleware"] = "active"
        return response


class AuthMiddleware(Middleware):
    def process_request(self, request):
        if request.headers.get("Authorization") != "secret":
            return Response("Unauthorized", status=401)
        return None


def test_middleware_pipeline():
    app = BustAPI()
    app.middleware_manager.add(HeaderMiddleware())

    @app.route("/test")
    def test_route():
        return "ok"

    client = app.test_client()
    resp = client.get("/test")
    assert resp.status_code == 200
    assert resp.text == "ok"
    assert resp.headers["X-Middleware"] == "active"


def test_middleware_interception():
    app = BustAPI()
    app.middleware_manager.add(AuthMiddleware())

    @app.route("/protected")
    def protected():
        return "secret data"

    client = app.test_client()

    # Test unauthorized
    resp = client.get("/protected")
    assert resp.status_code == 401
    assert resp.text == "Unauthorized"

    # Test authorized
    resp = client.get("/protected", headers={"Authorization": "secret"})
    assert resp.status_code == 200
    assert resp.text == "secret data"
