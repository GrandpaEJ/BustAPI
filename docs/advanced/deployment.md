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

### Free-Threaded Mode (Python 3.13t)

If you are using Python 3.13 free-threaded (nogil) mode, BustAPI automatically detects it. This allows your application to use all CPU cores from a single process without the Global Interpreter Lock (GIL).

This is ideal for heavy workloads where traditionally you would need to spawn multiple Gunicorn workers. With BustAPI + Python 3.13t, **one process** is often enough to saturate the machine.
