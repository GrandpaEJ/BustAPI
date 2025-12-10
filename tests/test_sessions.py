import pytest
from bustapi import BustAPI, Response, session


def test_session_lifecycle():
    app = BustAPI()
    app.secret_key = "test-secret"

    @app.route("/set")
    def set_session():
        session["user"] = "admin"
        return "set"

    @app.route("/get")
    def get_session():
        return session.get("user", "none")

    client = app.test_client()

    # Initial state
    resp = client.get("/get")
    assert resp.text == "none"

    # Set session
    resp = client.get("/set")
    assert "session" in resp.headers.get("Set-Cookie", "")

    # Verify cookie (simple verification that cookie is present)
    cookie_value = resp.headers["Set-Cookie"].split(";")[0]

    # Get session with cookie
    # Note: TestClient might need cookie jar support.
    # If BustAPI TestClient relies on requests Session, it should handle cookies automatically.
    # Let's check if TestClient uses requests.Session.

    # Assuming TestClient needs manual cookie handling if not fully implemented
    # But based on typical implementation, it might not persist cookies automatically
    # unless using a with client: block or session.
    # We'll pass the cookie manually for now to be safe.

    resp = client.get("/get", headers={"Cookie": cookie_value})
    assert resp.text == "admin"


def test_session_no_secret():
    app = BustAPI()
    # No secret key set

    @app.route("/fail")
    def fail():
        try:
            session["foo"] = "bar"
            return "ok"
        except RuntimeError:
            return "error"

    client = app.test_client()
    # Should probably log error or fail silently depending on implementation
    # Implementation: get_signing_serializer returns None if no secret key.
    # open_session returns None.
    # request.session is None.
    # session proxy raises RuntimeError if session is None.

    # Wait, open_session returns None if no signer?
    # verify logic:
    # if not app.secret_key: return None (serializer)
    # open_session: if s is None: return None
    # request.session = None
    # session proxy access -> RuntimeError("Session not available...")

    # But wrapper sets request.session = ...
    # So if wrapper sees None, it sets None.

    # So accessing it inside route should raise RuntimeError.

    # However, my proxy raises RuntimeError "ensure secret_key is set"

    # The route catches the RuntimeError and returns "error", so status should be 200
    resp = client.get("/fail")
    assert resp.status_code == 200
    assert resp.text == "error"
