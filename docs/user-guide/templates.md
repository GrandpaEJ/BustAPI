# Templates

Generating HTML directly in Python strings is tedious and dangerous (XSS vulnerabilities). BustAPI uses **Jinja2**, the most popular Python templating engine, for this purpose.

## Directory Structure

BustAPI expects a `templates` folder in the same directory as your application module.

```
/yourapp
    app.py
    /templates
        base.html
        index.html
    /static
        style.css
```

## Rendering

Use the `render_template` function. You can pass any number of keyword arguments to be available in the template context.

`render_template` returns a standard `Response` object with `Content-Type: text/html`, so you can return it directly from your view function.

```python
from bustapi import render_template

@app.route("/hello/<name>")
def hello(name):
    return render_template('index.html', name=name)
```

## Template Inheritance

The power of Jinja2 comes from inheritance. Define a base layout and extend it.

### base.html

```html
<!doctype html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

### index.html

```html
{% extends "base.html" %}

{% block title %}Home{% endblock %}

{% block content %}
    <h1>Welcome to my site</h1>
{% endblock %}
```
