from bustapi import BustAPI, Security

app = BustAPI()

# 1. Initialize Security
# This enables basic security middleware
security = Security(app)

# 2. Enable CORS
# Allow requests from any origin with GET/POST methods
security.enable_cors(origins="*", methods=["GET", "POST"])

# 3. Enable Security Headers
# Adds X-XSS-Protection, X-Frame-Options, etc.
security.enable_secure_headers()


@app.route("/")
def index():
    return {"message": "This endpoint has CORS and Security Headers enabled!"}


if __name__ == "__main__":
    print("Run this example and check headers with: curl -I http://127.0.0.1:5000/")
    app.run(port=5000)
