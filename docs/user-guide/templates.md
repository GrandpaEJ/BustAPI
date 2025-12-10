# Templates

BustAPI includes support for the **Jinja2** template engine, the same one used by Flask. This allows you to separate your HTML structure from your Python logic.

## Configuration

By default, BustAPI looks for templates in a `templates/` folder relative to your application.

```
/myapp
    app.py
    templates/
        index.html
```

You can customize this path:

```python
app = BustAPI(template_folder="my_templates")
```

## Rendering Templates

Use the `render_template` function to render HTML and pass variables (context).

```python title="app.py"
from bustapi import BustAPI, render_template

app = BustAPI()

@app.route("/hello/<name>")
def hello(name):
    return render_template("index.html", user=name)
```

```html title="templates/index.html"
<!DOCTYPE html>
<title>Hello from BustAPI</title>
{% if user %}
<h1>Hello {{ user }}!</h1>
{% else %}
<h1>Hello, World!</h1>
{% endif %}
```

## Template Syntax

Jinja2 is powerful. Some common syntax:

- **`{{ variable }}`**: Output a variable.
- **`{% if condition %}`**: Conditional logic.
- **`{% for item in list %}`**: Loops.
- **`{# comment #}`**: Comments.

Refer to the [Jinja2 Documentation](https://jinja.palletsprojects.com/) for full details.
