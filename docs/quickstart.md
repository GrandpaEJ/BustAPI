# Quickstart

Let's build a minimal "Hello World" application.

## 1. Create `app.py`

```python
from bustapi import BustAPI

app = BustAPI()

@app.route("/")
def home():
    return "Hello, World!"

if __name__ == "__main__":
    app.run()
```

## 2. Run the application

```bash
python app.py
```

You should see output indicating the server is running on `http://127.0.0.1:5000`.

## 3. Visit the API

Open your browser to `http://127.0.0.1:5000/`. You should see:

```
Hello, World!
```
