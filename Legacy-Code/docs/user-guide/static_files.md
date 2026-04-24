# Static Files

Web applications often need to serve static files such as CSS, JavaScript, and images.

## Configuration

By default, BustAPI looks for static files in a `static/` folder and serves them at `/static`.

```
/myapp
    app.py
    static/
        style.css
```

You can customize the folder URL:

```python
app = BustAPI(static_folder="assets", static_url_path="/assets")
```

## Serving Files

Just place your files in the static folder. BustAPI handles the rest using its high-performance Rust backend.

**URL**: `http://localhost:5000/static/style.css`

## Security

BustAPI's static file handler is written in Rust and includes built-in security features:

- **Path Traversal Protection**: Prevents access to files outside the static folder (e.g., `../../etc/passwd`).
- **Hidden File Blocking**: Automatically blocks access to files starting with `.` (e.g., `.env`, `.git`).

> [!WARNING]
> While BustAPI is secure, never place sensitive files (like database credentials or source code) inside your static folder.
