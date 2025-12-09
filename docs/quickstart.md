# Quickstart

```python
from bustapi import BustAPI

app = BustAPI()

@app.route("/")
def home(request):
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run()
```
