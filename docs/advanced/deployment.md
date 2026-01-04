# Deployment

BustAPI uses a high-performance **Rust Actix-web server** built-in. Unlike Flask, you do **not** need a separate WSGI server like Gunicorn to get production-ready performance.

## Running in Production

You can run your BustAPI app directly.

```bash
# Provide port/host via arguments or env vars
python app.py
```

However, for robust process management (restarts, logging, multiple workers), usage of a process manager is recommended.

### Using Systemd

Create a unit file `/etc/systemd/system/myapp.service`:

```ini
[Unit]
Description=My BustAPI App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/myapp
ExecStart=/var/www/myapp/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```



## Alternative Servers

While the built-in Rust server is the most optimized for BustAPI, you can also run your application with standard ASGI or WSGI servers.

### Uvicorn (ASGI)

BustAPI provides an `asgi_app` entry point compatible with Uvicorn and other ASGI servers.

```bash
# Install uvicorn
pip install uvicorn

# Run using the CLI
uvicorn main:app.asgi_app --interface asgi3
```

Or programmatically:

```python
if __name__ == "__main__":
    app.run(server="uvicorn")
```

### Gunicorn (WSGI)

For traditional deployments, you can use Gunicorn. BustAPI behaves as a standard WSGI application.

```bash
# Install gunicorn
pip install gunicorn

# Run using the CLI
gunicorn main:app
```

Or programmatically:

```python
if __name__ == "__main__":
    app.run(server="gunicorn")
```
