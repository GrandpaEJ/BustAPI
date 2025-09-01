# Quick Start Guide

Get up and running with BustAPI in minutes!

## Your First BustAPI App

Create a file called `app.py`:

```python
from bustapi import BustAPI

app = BustAPI()

@app.route('/')
def hello_world():
    return {'message': 'Hello, World!'}

if __name__ == '__main__':
    app.run(debug=True)
```

Run your app:

```bash
python app.py
```

Visit `http://127.0.0.1:8000` to see your app in action!

## Basic Routing

### Simple Routes

```python
from bustapi import BustAPI

app = BustAPI()

@app.route('/')
def home():
    return {'page': 'home'}

@app.route('/about')
def about():
    return {'page': 'about'}

@app.route('/contact')
def contact():
    return {'page': 'contact'}
```

### HTTP Methods

```python
@app.route('/users', methods=['GET'])
def get_users():
    return {'users': []}

@app.route('/users', methods=['POST'])
def create_user():
    return {'message': 'User created'}, 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    return {'message': f'User {user_id} updated'}

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    return {'message': f'User {user_id} deleted'}
```

### URL Parameters

```python
# String parameter
@app.route('/users/<username>')
def show_user(username):
    return {'username': username}

# Integer parameter
@app.route('/posts/<int:post_id>')
def show_post(post_id):
    return {'post_id': post_id}

# Float parameter
@app.route('/price/<float:price>')
def show_price(price):
    return {'price': price}

# Path parameter (accepts slashes)
@app.route('/files/<path:filename>')
def show_file(filename):
    return {'filename': filename}
```

## Request Handling

### Accessing Request Data

```python
from bustapi import BustAPI, request

app = BustAPI()

@app.route('/data', methods=['POST'])
def handle_data():
    # Get JSON data
    json_data = request.get_json()
    
    # Get form data
    form_data = request.form
    
    # Get query parameters
    args = request.args
    
    # Get headers
    headers = request.headers
    
    return {
        'json': json_data,
        'form': dict(form_data),
        'args': dict(args),
        'headers': dict(headers)
    }
```

### File Uploads

```python
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No file selected'}, 400
    
    # Save file
    file.save(f'uploads/{file.filename}')
    return {'message': 'File uploaded successfully'}
```

## Response Types

### JSON Responses

```python
from bustapi import jsonify

@app.route('/json')
def json_response():
    return jsonify({
        'message': 'Hello, JSON!',
        'status': 'success',
        'data': [1, 2, 3, 4, 5]
    })
```

### Custom Status Codes

```python
@app.route('/created', methods=['POST'])
def create_resource():
    return {'message': 'Resource created'}, 201

@app.route('/not-found')
def not_found():
    return {'error': 'Resource not found'}, 404
```

### Custom Headers

```python
from bustapi import make_response

@app.route('/custom-headers')
def custom_headers():
    response = make_response({'message': 'Custom headers'})
    response.headers['X-Custom-Header'] = 'BustAPI'
    response.headers['X-API-Version'] = '1.0'
    return response
```

## Error Handling

```python
from bustapi import BustAPI, abort

app = BustAPI()

@app.route('/users/<int:user_id>')
def get_user(user_id):
    if user_id < 1:
        abort(400, description="Invalid user ID")
    
    if user_id > 1000:
        abort(404, description="User not found")
    
    return {'user_id': user_id, 'name': f'User {user_id}'}

@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found', 'message': str(error)}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500
```

## Configuration

```python
app = BustAPI()

# Development configuration
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'your-secret-key'

# Custom configuration
app.config['DATABASE_URL'] = 'sqlite:///app.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/config')
def show_config():
    return {
        'debug': app.config.get('DEBUG'),
        'upload_folder': app.config.get('UPLOAD_FOLDER')
    }
```

## Running Your App

### Development Server

```python
if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=8000,
        debug=True
    )
```

### Production Server

```bash
# Using gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Using uvicorn
pip install uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Next Steps

- Learn about [Advanced Features](advanced.md)
- Explore [Template Rendering](templates.md)
- Check out [Flask Compatibility](flask-compatibility.md)
- Browse [Examples](../examples/)
