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

## Control Structures

Jinja2 supports standard control structures like loops and conditionals.

### Loops

Iterate over lists or dictionaries passed to the template.

```html
<ul>
{% for user in users %}
    <li>{{ user.name }}</li>
{% else %}
    <li>No users found.</li>
{% endfor %}
</ul>
```

### Conditionals

Conditionally render content based on variables.

```html
{% if current_user.is_authenticated %}
    <p>Welcome, {{ current_user.name }}!</p>
{% else %}
    <p>Please log in.</p>
{% endif %}
```

## Filters

Filters allow you to modify variables for display. They are separated from the variable by a pipe symbol (`|`).

```html
<!-- Capitalize the name -->
<h1>{{ title|upper }}</h1>

<!-- Default value if variable is undefined/empty -->
<p>Bio: {{ bio|default('No bio provided') }}</p>

<!-- Safe HTML (disable escaping) -->
<div>{{ unsafe_html_content|safe }}</div>
```

## Generating URLs

Use `url_for()` to generate URLs for your routes and static files. This ensures your links remain valid even if you change your URL patterns.

```html
<!-- Link to a route -->
<a href="{{ url_for('user_profile', id=42) }}">View Profile</a>

<!-- Link to a static file (CSS/JS/Images) -->
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
<script src="{{ url_for('static', filename='app.js') }}"></script>
```

> [!NOTE]
> Ensure your routes have an `endpoint` name defined in `@app.route(..., endpoint='name')` or implicitly use the function name.

## Including Templates

You can include reusable partials (like headers, footers, or widgets) using `{% include %}`.

```html
<body>
    {% include 'header.html' %}
    
    <div class="content">
        ...
    </div>
    
    {% include 'footer.html' %}
</body>
```

