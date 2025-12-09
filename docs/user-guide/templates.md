# Templates

BustAPI integrates **Jinja2** for proper HTML rendering.

## Setup

Create a `templates/` folder in your project root.

## Usage

```python
from bustapi import BustAPI, render_template

app = BustAPI()

@app.route("/hello/<name>")
def hello(request, name):
    return render_template("hello.html", name=name)
```

## Template Example (`templates/hello.html`)

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Hello</title>
  </head>
  <body>
    <h1>Hello, {{ name }}!</h1>
  </body>
</html>
```
