#!/usr/bin/env python3
"""
URL Routing Examples

This example demonstrates various URL routing patterns in BustAPI:
- Static routes
- Dynamic routes with parameters
- Different parameter types (string, int, float, path)
- Query parameters
- Multiple routes for the same function
"""

from bustapi import BustAPI, request

app = BustAPI()

# Static routes
@app.route('/')
def home():
    """Home page"""
    return {'page': 'home', 'message': 'Welcome to BustAPI routing examples!'}

@app.route('/about')
def about():
    """About page"""
    return {'page': 'about', 'description': 'BustAPI routing demonstration'}

# String parameters
@app.route('/users/<username>')
def show_user_profile(username):
    """Show user profile by username"""
    return {
        'user': username,
        'profile_url': f'/users/{username}',
        'type': 'string_parameter'
    }

# Integer parameters
@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Show post by ID"""
    return {
        'post_id': post_id,
        'title': f'Post #{post_id}',
        'type': 'integer_parameter'
    }

# Float parameters
@app.route('/products/<float:price>')
def products_by_price(price):
    """Show products by price"""
    return {
        'max_price': price,
        'currency': 'USD',
        'type': 'float_parameter'
    }

# Path parameters (accepts slashes)
@app.route('/files/<path:filename>')
def show_file(filename):
    """Show file by path"""
    return {
        'filename': filename,
        'full_path': f'/files/{filename}',
        'type': 'path_parameter'
    }

# Multiple parameters
@app.route('/users/<username>/posts/<int:post_id>')
def show_user_post(username, post_id):
    """Show specific post by user"""
    return {
        'username': username,
        'post_id': post_id,
        'url': f'/users/{username}/posts/{post_id}',
        'type': 'multiple_parameters'
    }

# Query parameters
@app.route('/search')
def search():
    """Search with query parameters"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    return {
        'query': query,
        'page': page,
        'per_page': per_page,
        'results': f'Search results for "{query}"',
        'type': 'query_parameters'
    }

# Multiple routes for same function
@app.route('/api/v1/status')
@app.route('/api/status')
@app.route('/status')
def api_status():
    """API status endpoint with multiple routes"""
    return {
        'status': 'healthy',
        'version': '1.0.0',
        'uptime': '24h',
        'available_routes': [
            '/api/v1/status',
            '/api/status', 
            '/status'
        ]
    }

# Route with trailing slash handling
@app.route('/docs/')
def documentation():
    """Documentation page"""
    return {
        'page': 'documentation',
        'note': 'This route handles trailing slashes',
        'url': '/docs/'
    }

# Catch-all route (should be last)
@app.route('/<path:path>')
def catch_all(path):
    """Catch-all route for undefined paths"""
    return {
        'error': 'Route not found',
        'requested_path': f'/{path}',
        'available_routes': [
            '/',
            '/about',
            '/users/<username>',
            '/posts/<int:post_id>',
            '/products/<float:price>',
            '/files/<path:filename>',
            '/users/<username>/posts/<int:post_id>',
            '/search?q=<query>&page=<page>&per_page=<per_page>',
            '/status',
            '/docs/'
        ]
    }, 404

if __name__ == '__main__':
    print("🚀 Starting BustAPI Routing Examples...")
    print("\n📍 Try these URLs:")
    print("   http://127.0.0.1:8000/")
    print("   http://127.0.0.1:8000/users/john")
    print("   http://127.0.0.1:8000/posts/123")
    print("   http://127.0.0.1:8000/products/29.99")
    print("   http://127.0.0.1:8000/files/docs/readme.txt")
    print("   http://127.0.0.1:8000/users/alice/posts/456")
    print("   http://127.0.0.1:8000/search?q=python&page=2&per_page=5")
    print("   http://127.0.0.1:8000/status")
    
    app.run(host='127.0.0.1', port=8000, debug=True)
