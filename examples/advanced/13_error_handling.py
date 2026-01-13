"""
Example 13: Error Handling
========================

This example demonstrates how to handle errors and exceptions in BustAPI.
"""

from bustapi import BustAPI, abort, jsonify

app = BustAPI()


# 1. Custom Error Handler for standard HTTP errors (e.g. 404)
@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Resource not found", code=404), 404


# 2. Custom Error Handler for specific exceptions
class ValidationException(Exception):
    pass


@app.errorhandler(ValidationException)
def handle_validation_error(e):
    return jsonify(error=str(e), type="validation_error"), 400


@app.route("/")
def home():
    return {
        "message": "Error Handling Demo",
        "routes": [
            "/abort/401 - trigger 401 via abort()",
            "/abort/404 - trigger 404 via abort()",
            "/error - raise generic exception",
            "/validate/<int:value> - raises ValidationException if value < 0",
        ],
    }


@app.route("/abort/<int:code>")
def trigger_abort(code):
    # abort() stops request and returns error response
    abort(code)


@app.route("/error")
def trigger_error():
    # Unhandled exceptions return 500 Internal Server Error
    raise Exception("Something went wrong!")


@app.route("/validate/<int:value>")
def validate(value):
    if value < 0:
        raise ValidationException("Value must be non-negative")
    return {"status": "valid", "value": value}


if __name__ == "__main__":
    app.run(debug=True)
