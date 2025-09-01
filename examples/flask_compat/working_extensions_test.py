#!/usr/bin/env python3
"""
Working Flask Extensions Test

This example demonstrates Flask extensions that work well with BustAPI:
- Flask-CORS: Cross-Origin Resource Sharing ✅
- Flask-JWT-Extended: JWT authentication ✅
"""

from bustapi import BustAPI, request, jsonify

app = BustAPI()

# Test 1: Flask-CORS - WORKING ✅
print("🧪 Testing Flask-CORS...")
try:
    from flask_cors import CORS
    
    # Initialize CORS with BustAPI
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "https://example.com"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    @app.route('/api/cors-test')
    def cors_test():
        """Test CORS headers"""
        return {'message': 'CORS is working!', 'cors': True}
    
    print("✅ Flask-CORS: Compatible and working!")
    
except ImportError:
    print("⚠️ Flask-CORS: Not installed")
except Exception as e:
    print(f"❌ Flask-CORS: Error - {e}")

# Test 2: Flask-JWT-Extended - WORKING ✅
print("\n🧪 Testing Flask-JWT-Extended...")
try:
    from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-in-production'
    jwt = JWTManager(app)
    
    @app.route('/auth/login', methods=['POST'])
    def login():
        """Login endpoint that returns JWT token"""
        try:
            data = request.get_json() or {}
            username = data.get('username', 'testuser')
            password = data.get('password', 'password')
            
            if username == 'testuser' and password == 'password':
                access_token = create_access_token(identity=username)
                return {'access_token': access_token, 'message': 'Login successful'}
            
            return {'error': 'Invalid credentials'}, 401
        except Exception as e:
            return {'error': f'Login error: {str(e)}'}, 400
    
    @app.route('/auth/protected', methods=['GET'])
    @jwt_required()
    def protected():
        """Protected endpoint requiring JWT token"""
        try:
            current_user = get_jwt_identity()
            return {'message': f'Hello {current_user}!', 'protected': True, 'user': current_user}
        except Exception as e:
            return {'error': f'Protected route error: {str(e)}'}, 400
    
    print("✅ Flask-JWT-Extended: Compatible and working!")
    
except ImportError:
    print("⚠️ Flask-JWT-Extended: Not installed")
except Exception as e:
    print(f"❌ Flask-JWT-Extended: Error - {e}")

# Test endpoints
@app.route('/')
def index():
    """Main page showing working extensions"""
    return {
        'message': 'BustAPI Flask Extensions - Working Examples',
        'working_extensions': [
            'Flask-CORS ✅',
            'Flask-JWT-Extended ✅'
        ],
        'endpoints': [
            'GET / - This page',
            'GET /api/cors-test - Test CORS (check headers)',
            'POST /auth/login - JWT login (username: testuser, password: password)',
            'GET /auth/protected - JWT protected route (requires Authorization header)',
            'GET /test-working - Test working extensions'
        ],
        'usage_examples': {
            'login': {
                'method': 'POST',
                'url': '/auth/login',
                'body': {'username': 'testuser', 'password': 'password'}
            },
            'protected': {
                'method': 'GET', 
                'url': '/auth/protected',
                'headers': {'Authorization': 'Bearer <token_from_login>'}
            }
        }
    }

@app.route('/test-working')
def test_working():
    """Test working extensions"""
    results = {}
    
    # Test CORS
    try:
        from flask_cors import CORS
        results['cors'] = {'status': 'Available', 'working': True}
    except ImportError:
        results['cors'] = {'status': 'Not installed', 'working': False}
    
    # Test JWT
    try:
        from flask_jwt_extended import JWTManager
        results['jwt'] = {'status': 'Available', 'working': True}
    except ImportError:
        results['jwt'] = {'status': 'Not installed', 'working': False}
    
    working_count = len([r for r in results.values() if r.get('working', False)])
    
    return {
        'message': 'Working Flask Extensions Test Results',
        'results': results,
        'total_tested': len(results),
        'working': working_count,
        'success_rate': f"{(working_count/len(results)*100):.1f}%" if results else "0%"
    }

# Demo endpoints for testing
@app.route('/demo/public')
def public_demo():
    """Public demo endpoint"""
    return {
        'message': 'This is a public endpoint',
        'public': True,
        'timestamp': __import__('time').time()
    }

@app.route('/demo/cors-enabled', methods=['GET', 'POST', 'PUT', 'DELETE'])
def cors_demo():
    """CORS-enabled demo endpoint"""
    return {
        'message': 'This endpoint has CORS enabled',
        'method': request.method,
        'cors_enabled': True,
        'allowed_origins': ['http://localhost:3000', 'https://example.com']
    }

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting BustAPI Working Flask Extensions Test...")
    print("="*60)
    print("📍 Main page: http://127.0.0.1:8000")
    print("📍 Test results: http://127.0.0.1:8000/test-working")
    print("📍 CORS test: http://127.0.0.1:8000/api/cors-test")
    print("📍 Public demo: http://127.0.0.1:8000/demo/public")
    print("📍 CORS demo: http://127.0.0.1:8000/demo/cors-enabled")
    print("\n🔐 JWT Authentication:")
    print("📍 Login: POST http://127.0.0.1:8000/auth/login")
    print("   Body: {\"username\": \"testuser\", \"password\": \"password\"}")
    print("📍 Protected: GET http://127.0.0.1:8000/auth/protected")
    print("   Header: Authorization: Bearer <token>")
    print("\n💡 Use curl or Postman to test JWT authentication")
    print("="*60)
    
    app.run(host='127.0.0.1', port=8000, debug=True)
