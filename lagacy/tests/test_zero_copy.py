import json

from bustapi import BustAPI, Response


def test_request_body_integrity():
    app = BustAPI()

    @app.route("/echo", methods=["POST"])
    def echo_body():
        # Access body via request.data using the global proxy
        from bustapi import request

        data = request.data
        return Response(data, status=200)

    client = app.test_client()
    payload = b"Hello, World!" * 100
    resp = client.post("/echo", data=payload)
    assert resp.status_code == 200
    assert resp.text.encode("utf-8") == payload


def test_json_parsing():
    app = BustAPI()

    @app.route("/json", methods=["POST"])
    def parse_json():
        try:
            from bustapi import request

            data = request.get_json()
            if data is None:
                return Response("JSON is None", status=400)
            return Response(
                json.dumps(data), headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            return Response(f"Error: {e}", status=500)

    client = app.test_client()
    payload = {"key": "value", "numbers": [1, 2, 3]}
    resp = client.post(
        "/json", data=json.dumps(payload), headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 200, f"Status: {resp.status_code}, Body: {resp.text}"
    assert resp.json == payload
