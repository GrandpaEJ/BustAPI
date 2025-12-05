#!/usr/bin/env python3
"""
Jinja2 Template Rendering Example

This example demonstrates how to use Jinja2 templates with BustAPI:
- Basic template rendering
- Template variables
- Template inheritance
- Template filters
- Static file serving
"""

import os

from bustapi import BustAPI, request

app = BustAPI()

# Configure template directory
app.template_folder = "examples/templates/templates"
app.static_folder = "examples/templates/static"


@app.route("/")
def index():
    """Home page with template"""
    if request.wants_json():
        return {"title": "BustAPI Templates", "message": "Welcome to BustAPI with Jinja2!"}

    return app.render_template(
        "index.html",
        title="BustAPI Templates",
        message="Welcome to BustAPI with Jinja2!",
    )


@app.route("/users")
def users_list():
    """Users list page"""
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "active": False},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "active": True},
    ]

    if request.wants_json():
        return {"users": users, "total_users": len(users)}

    return app.render_template(
        "users.html",
        title="Users List",
        users=users,
        total_users=len(users),
    )


@app.route("/users/<int:user_id>")
def user_detail(user_id):
    """User detail page"""
    # Mock user data
    users = {
        1: {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com",
            "bio": "Software Developer",
        },
        2: {
            "id": 2,
            "name": "Bob",
            "email": "bob@example.com",
            "bio": "Data Scientist",
        },
        3: {
            "id": 3,
            "name": "Charlie",
            "email": "charlie@example.com",
            "bio": "Product Manager",
        },
    }

    user = users.get(user_id)
    if not user:
        if request.wants_json():
            return {"error": "User not found"}, 404
        return app.render_template("404.html", title="User Not Found"), 404

    if request.wants_json():
        return user

    return app.render_template("user_detail.html", title=f'User: {user["name"]}', user=user)


@app.route("/form")
def contact_form():
    """Contact form page"""
    if request.wants_json():
        return {"title": "Contact Form", "fields": ["name", "email", "message"]}

    return app.render_template("form.html", title="Contact Form")


@app.route("/form", methods=["POST"])
def handle_form():
    """Handle form submission"""
    name = request.form.get("name", "")
    email = request.form.get("email", "")
    message = request.form.get("message", "")

    # In a real app, you'd save this to a database
    if request.wants_json():
        return {"status": "success", "name": name, "email": email, "message": message}

    return app.render_template(
        "form_success.html",
        title="Form Submitted",
        name=name,
        email=email,
        message=message,
    )


@app.route("/dashboard")
def dashboard():
    """Dashboard with charts and data"""
    stats = {
        "total_users": 150,
        "active_users": 120,
        "total_posts": 450,
        "total_comments": 1200,
    }

    recent_activity = [
        {"user": "Alice", "action": "Created a new post", "time": "2 minutes ago"},
        {"user": "Bob", "action": "Commented on a post", "time": "5 minutes ago"},
        {"user": "Charlie", "action": "Updated profile", "time": "10 minutes ago"},
    ]

    if request.wants_json():
        return {"stats": stats, "recent_activity": recent_activity}

    return app.render_template(
        "dashboard.html",
        title="Dashboard",
        stats=stats,
        recent_activity=recent_activity,
    )


@app.route("/blog")
def blog():
    """Blog listing page"""
    posts = [
        {
            "id": 1,
            "title": "Getting Started with BustAPI",
            "author": "Alice",
            "date": "2024-01-15",
            "excerpt": "Learn how to build high-performance web applications with BustAPI.",
            "tags": ["python", "web", "performance"],
        },
        {
            "id": 2,
            "title": "Template Rendering in BustAPI",
            "author": "Bob",
            "date": "2024-01-10",
            "excerpt": "Discover how to use Jinja2 templates effectively in your BustAPI applications.",
            "tags": ["templates", "jinja2", "frontend"],
        },
        {
            "id": 3,
            "title": "Building REST APIs with BustAPI",
            "author": "Charlie",
            "date": "2024-01-05",
            "excerpt": "Create robust REST APIs using BustAPI's powerful routing system.",
            "tags": ["api", "rest", "backend"],
        },
    ]

    if request.wants_json():
        return {"posts": posts}

    return app.render_template("blog.html", title="Blog", posts=posts)


@app.route("/blog/<int:post_id>")
def blog_post(post_id):
    """Individual blog post"""
    posts = {
        1: {
            "id": 1,
            "title": "Getting Started with BustAPI",
            "author": "Alice",
            "date": "2024-01-15",
            "content": """
            <p>BustAPI is a high-performance Python web framework that combines the ease of Flask with the speed of Rust.</p>
            <p>In this post, we'll explore how to get started with BustAPI and build your first application.</p>
            <h3>Installation</h3>
            <p>Installing BustAPI is simple with pip:</p>
            <pre><code>pip install bustapi</code></pre>
            """,
            "tags": ["python", "web", "performance"],
        },
        2: {
            "id": 2,
            "title": "Template Rendering in BustAPI",
            "author": "Bob",
            "date": "2024-01-10",
            "content": """
            <p>BustAPI supports Jinja2 template rendering out of the box.</p>
            <p>This makes it easy to create dynamic web pages with server-side rendering.</p>
            <h3>Basic Usage</h3>
            <p>Use the render_template function to render templates:</p>
            <pre><code>from bustapi import render_template

@app.route('/')
def index():
    return render_template('index.html', title='My App')</code></pre>
            """,
            "tags": ["templates", "jinja2", "frontend"],
        },
    }

    post = posts.get(post_id)
    if not post:
        if request.wants_json():
            return {"error": "Post not found"}, 404
        return app.render_template("404.html", title="Post Not Found"), 404

    if request.wants_json():
        return post

    return app.render_template("blog_post.html", title=post["title"], post=post)


@app.route("/content-demo")
def content_demo():
    """Demonstrate different content types based on Accept header"""
    if request.wants_json():
        return {
            "type": "json",
            "message": "This is JSON content",
            "supported_types": ["text", "html", "xml", "json", "image", "audio", "video", "font", "application"]
        }
    elif request.wants_xml():
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <type>xml</type>
    <message>This is XML content</message>
    <supported_types>
        <type>text</type>
        <type>html</type>
        <type>xml</type>
        <type>json</type>
        <type>image</type>
        <type>audio</type>
        <type>video</type>
        <type>font</type>
        <type>application</type>
    </supported_types>
</response>"""
        from bustapi.response import xmlify
        return xmlify(xml_content)
    elif request.wants_text():
        from bustapi.response import textify
        return textify("This is plain text content. Supported content types: text, html, xml, json, image, audio, video, font, application")
    elif request.wants_html():
        html_content = """<!DOCTYPE html>
<html>
<head><title>Content Demo</title></head>
<body>
    <h1>HTML Content</h1>
    <p>This is HTML content.</p>
    <p>Supported content types:</p>
    <ul>
        <li>text</li>
        <li>html</li>
        <li>xml</li>
        <li>json</li>
        <li>image</li>
        <li>audio</li>
        <li>video</li>
        <li>font</li>
        <li>application</li>
    </ul>
</body>
</html>"""
        from bustapi.response import htmlify
        return htmlify(html_content)
    else:
        # Default to JSON
        return {
            "type": "default_json",
            "message": "Default JSON response - specify Accept header for different content types",
            "supported_types": ["text", "html", "xml", "json", "image", "audio", "video", "font", "application"]
        }


if __name__ == "__main__":
    # Create template directories if they don't exist
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)

    print("🚀 Starting BustAPI Template Example...")
    print("📁 Make sure you have the template files in the 'templates' directory")
    print("📍 Visit: http://127.0.0.1:8003")

    app.run(host="127.0.0.1", port=8003, debug=True)
