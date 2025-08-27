"""
Simple Hello World example for BustAPI

This example demonstrates basic BustAPI usage with both sync and async routes.
"""

from bustapi import BustAPI

app = BustAPI()

@app.route('/')
def hello():
    """Simple hello world route."""
    return {'message': 'Hello, World! meo'}

@app.route('/greet/<name>')
def greet(name):
    """Greeting with path parameter."""
    return {'message': f'Hello, {name}!'}

@app.route('/async')
async def async_hello():
    """Async route example."""
    import asyncio
    await asyncio.sleep(0.1)  # Simulate async work
    return {'message': 'Hello from async!'}

@app.route('/json', methods=['GET', 'POST'])
def json_endpoint():
    """JSON endpoint that handles both GET and POST."""
    from bustapi import request
    
    if request.method == 'GET':
        return {'method': 'GET', 'message': 'Send me some JSON!'}
    
    # POST request
    data = request.json
    return {
        'method': 'POST',
        'received': data,
        'message': 'Thanks for the JSON!'
    }

@app.route('/form', methods=['POST'])
def form_endpoint():
    """Form data endpoint."""
    from bustapi import request
    
    name = request.form.get('name', 'Anonymous')
    email = request.form.get('email', '')
    
    return {
        'message': f'Hello, {name}!',
        'email': email,
        'form_data': dict(request.form)
    }

@app.route('/headers')
def headers_endpoint():
    """Display request headers."""
    from bustapi import request
    
    return {
        'headers': dict(request.headers),
        'user_agent': request.user_agent,
        'method': request.method,
        'path': request.path
    }

# Error handler example
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found', 'message': 'The requested resource was not found.'}, 404

if __name__ == '__main__':
    print("🚀 Starting BustAPI Hello World server...")
    print("📝 Available endpoints:")
    print("   GET  /               - Hello world")
    print("   GET  /greet/<name>   - Personalized greeting")
    print("   GET  /async          - Async endpoint")
    print("   GET  /json           - JSON endpoint info")
    print("   POST /json           - Send JSON data")
    print("   POST /form           - Form data endpoint")
    print("   GET  /headers        - View request headers")
    print()
    
    try:
        app.run(host='127.0.0.1', port=5090, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")