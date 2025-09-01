
from flask import Flask, jsonify
import time

app = Flask(__name__)

users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
]

@app.route('/')
def root():
    return jsonify({
        'message': 'Flask Benchmark Server',
        'version': '1.0.0',
        'timestamp': time.time(),
        'status': 'running'
    })

@app.route('/api/test')
def api_test():
    return jsonify({
        'test': True,
        'framework': 'Flask',
        'performance': 'baseline',
        'timestamp': time.time()
    })

@app.route('/api/users')
def get_users():
    return jsonify({
        'users': users,
        'count': len(users),
        'timestamp': time.time()
    })

if __name__ == '__main__':
    print("🚀 Starting Flask Benchmark Server...")
    app.run(host='127.0.0.1', port=8000, debug=False)
