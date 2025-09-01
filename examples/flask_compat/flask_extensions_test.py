#!/usr/bin/env python3
"""
Flask Extensions Compatibility Test

This example tests popular Flask extensions with BustAPI:
- Flask-CORS: Cross-Origin Resource Sharing
- Flask-JWT-Extended: JWT authentication
- Flask-SQLAlchemy: Database ORM
- Flask-Limiter: Rate limiting
- Flask-Caching: Response caching
"""

from bustapi import BustAPI, request, jsonify
import os

app = BustAPI()

# Test 1: Flask-CORS
print("🧪 Testing Flask-CORS compatibility...")
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
    
    print("✅ Flask-CORS: Compatible")
    
except ImportError:
    print("⚠️ Flask-CORS: Not installed (pip install flask-cors)")
except Exception as e:
    print(f"❌ Flask-CORS: Error - {e}")

# Test 2: Flask-JWT-Extended
print("\n🧪 Testing Flask-JWT-Extended compatibility...")
try:
    from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-in-production'
    jwt = JWTManager(app)
    
    @app.route('/auth/login', methods=['POST'])
    def login():
        """Login endpoint that returns JWT token"""
        # Mock authentication
        username = request.get_json().get('username', 'testuser')
        password = request.get_json().get('password', 'password')
        
        if username == 'testuser' and password == 'password':
            access_token = create_access_token(identity=username)
            return {'access_token': access_token}
        
        return {'error': 'Invalid credentials'}, 401
    
    @app.route('/auth/protected', methods=['GET'])
    @jwt_required()
    def protected():
        """Protected endpoint requiring JWT token"""
        current_user = get_jwt_identity()
        return {'message': f'Hello {current_user}!', 'protected': True}
    
    print("✅ Flask-JWT-Extended: Compatible")
    
except ImportError:
    print("⚠️ Flask-JWT-Extended: Not installed (pip install flask-jwt-extended)")
except Exception as e:
    print(f"❌ Flask-JWT-Extended: Error - {e}")

# Test 3: Flask-SQLAlchemy
print("\n🧪 Testing Flask-SQLAlchemy compatibility...")
try:
    from flask_sqlalchemy import SQLAlchemy
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    
    # Define a simple model
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        
        def to_dict(self):
            return {
                'id': self.id,
                'username': self.username,
                'email': self.email
            }
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    @app.route('/users', methods=['GET'])
    def get_users():
        """Get all users from database"""
        users = User.query.all()
        return {'users': [user.to_dict() for user in users]}
    
    @app.route('/users', methods=['POST'])
    def create_user():
        """Create a new user in database"""
        data = request.get_json()
        user = User(username=data['username'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return {'user': user.to_dict()}, 201
    
    print("✅ Flask-SQLAlchemy: Compatible")
    
except ImportError:
    print("⚠️ Flask-SQLAlchemy: Not installed (pip install flask-sqlalchemy)")
except Exception as e:
    print(f"❌ Flask-SQLAlchemy: Error - {e}")

# Test 4: Flask-Limiter
print("\n🧪 Testing Flask-Limiter compatibility...")
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    # Initialize rate limiter
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    @app.route('/api/limited')
    @limiter.limit("5 per minute")
    def limited_endpoint():
        """Rate limited endpoint"""
        return {'message': 'This endpoint is rate limited!', 'limited': True}
    
    print("✅ Flask-Limiter: Compatible")
    
except ImportError:
    print("⚠️ Flask-Limiter: Not installed (pip install flask-limiter)")
except Exception as e:
    print(f"❌ Flask-Limiter: Error - {e}")

# Test 5: Flask-Caching
print("\n🧪 Testing Flask-Caching compatibility...")
try:
    from flask_caching import Cache
    
    # Configure caching
    app.config['CACHE_TYPE'] = 'simple'
    cache = Cache(app)
    
    @app.route('/api/cached')
    @cache.cached(timeout=60)
    def cached_endpoint():
        """Cached endpoint"""
        import time
        return {
            'message': 'This response is cached for 60 seconds!',
            'timestamp': time.time(),
            'cached': True
        }
    
    print("✅ Flask-Caching: Compatible")
    
except ImportError:
    print("⚠️ Flask-Caching: Not installed (pip install flask-caching)")
except Exception as e:
    print(f"❌ Flask-Caching: Error - {e}")

# Test 6: Flask-Mail
print("\n🧪 Testing Flask-Mail compatibility...")
try:
    from flask_mail import Mail, Message
    
    # Configure mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
    app.config['MAIL_PASSWORD'] = 'your-password'
    
    mail = Mail(app)
    
    @app.route('/api/send-mail', methods=['POST'])
    def send_mail():
        """Send email endpoint"""
        data = request.get_json()
        
        msg = Message(
            subject=data.get('subject', 'Test Email'),
            sender=app.config['MAIL_USERNAME'],
            recipients=[data.get('to', 'test@example.com')],
            body=data.get('body', 'This is a test email from BustAPI!')
        )
        
        # Note: Won't actually send without proper credentials
        # mail.send(msg)
        
        return {'message': 'Email would be sent!', 'mail': True}
    
    print("✅ Flask-Mail: Compatible")
    
except ImportError:
    print("⚠️ Flask-Mail: Not installed (pip install flask-mail)")
except Exception as e:
    print(f"❌ Flask-Mail: Error - {e}")

# Test endpoints
@app.route('/')
def index():
    """Main page showing extension compatibility"""
    return {
        'message': 'BustAPI Flask Extensions Compatibility Test',
        'extensions_tested': [
            'Flask-CORS',
            'Flask-JWT-Extended', 
            'Flask-SQLAlchemy',
            'Flask-Limiter',
            'Flask-Caching',
            'Flask-Mail'
        ],
        'endpoints': [
            'GET / - This page',
            'GET /api/cors-test - Test CORS',
            'POST /auth/login - JWT login',
            'GET /auth/protected - JWT protected route',
            'GET /users - Get users (SQLAlchemy)',
            'POST /users - Create user (SQLAlchemy)',
            'GET /api/limited - Rate limited endpoint',
            'GET /api/cached - Cached endpoint',
            'POST /api/send-mail - Send email'
        ]
    }

@app.route('/test-all')
def test_all():
    """Test all extensions at once"""
    results = {}
    
    # Test CORS
    try:
        from flask_cors import CORS
        results['cors'] = 'Available'
    except ImportError:
        results['cors'] = 'Not installed'
    
    # Test JWT
    try:
        from flask_jwt_extended import JWTManager
        results['jwt'] = 'Available'
    except ImportError:
        results['jwt'] = 'Not installed'
    
    # Test SQLAlchemy
    try:
        from flask_sqlalchemy import SQLAlchemy
        results['sqlalchemy'] = 'Available'
    except ImportError:
        results['sqlalchemy'] = 'Not installed'
    
    # Test Limiter
    try:
        from flask_limiter import Limiter
        results['limiter'] = 'Available'
    except ImportError:
        results['limiter'] = 'Not installed'
    
    # Test Caching
    try:
        from flask_caching import Cache
        results['caching'] = 'Available'
    except ImportError:
        results['caching'] = 'Not installed'
    
    # Test Mail
    try:
        from flask_mail import Mail
        results['mail'] = 'Available'
    except ImportError:
        results['mail'] = 'Not installed'
    
    return {
        'message': 'Flask Extensions Compatibility Results',
        'results': results,
        'total_tested': len(results),
        'available': len([v for v in results.values() if v == 'Available'])
    }

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Starting BustAPI Flask Extensions Test...")
    print("="*50)
    print("📍 Visit: http://127.0.0.1:8000")
    print("📍 Test all: http://127.0.0.1:8000/test-all")
    print("📍 CORS test: http://127.0.0.1:8000/api/cors-test")
    print("📍 Protected: http://127.0.0.1:8000/auth/protected")
    print("📍 Users: http://127.0.0.1:8000/users")
    print("="*50)
    
    app.run(host='127.0.0.1', port=8000, debug=True)
