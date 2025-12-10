from bustapi import BustAPI, RateLimit

app = BustAPI()

# Initialize Rate Limiter
limiter = RateLimit(app)


@app.route("/")
def home():
    return {"message": "I am not rate limited (unless global limit is set)"}


# Apply rate limit: 2 requests per 10 seconds
@app.route("/fast")
@limiter.limit("2/second")
def fast_endpoint():
    return {"message": "I allow 2 requests per second!"}


# Apply strict limit: 1 request per minute
@app.route("/slow")
@limiter.limit("1/minute")
def slow_endpoint():
    return {"message": "I only allow 1 request per minute. Don't spam me!"}


@app.before_request
def start_timer():
    import time

    from bustapi import request

    request.start_time = time.time()


@app.after_request
def log_request_info(response):
    import time

    from bustapi import logging, request

    duration = time.time() - getattr(request, "start_time", time.time())
    logging.log_request(request.method, request.path, response.status_code, duration)
    return response


@app.errorhandler(429)
def handle_ratelimit(e):
    import time

    from bustapi import logging, request

    duration = time.time() - getattr(request, "start_time", time.time())
    logging.log_request(request.method, request.path, 429, duration, error=str(e))
    return {"error": str(e)}, 429


if __name__ == "__main__":
    print("Starting Rate Limit Demo...")
    print("Try hitting http://127.0.0.1:5000/fast repeatedly.")
    app.run(port=5000)
