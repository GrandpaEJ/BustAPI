"""
Server execution adapters for BusAPI.
Handles running the application with various backends (Rust, Uvicorn, Gunicorn, Hypercorn).
"""

import multiprocessing
import os
import sys
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .app import BustAPI


def run_server(
    app: "BustAPI",
    host: str = "127.0.0.1",
    port: int = 5000,
    debug: bool = False,
    workers: Optional[int] = None,
    reload: bool = False,
    server: str = "rust",
    **options,
) -> None:
    """
    Run the application server.
    """
    if debug:
        # Auto-enable Request Logging in Debug Mode
        # Note: This requires access to app.before_request/after_request
        # Ideally this logic stays in app.py's run(), but if we move it here
        # we need to be careful. Let's assume app.py handles configuration
        # BEFORE calling this, or we handle it here.
        # Given the refactor, let's keep the logging setup in app.py or
        # accept that serving.py modifies the app.
        pass

    # Handle reload using Rust hot-reloader
    if reload or debug:
        if os.environ.get("BUSTAPI_RELOADER_RUN") != "true":
            try:
                from . import bustapi_core

                print(f"🔄 BustAPI Rust reloader active (using {server})")
                bustapi_core.enable_hot_reload(".")
                
                # Rust reloader spawns a thread, so we continue to run the server.
                # When a file changes, Rust will execvp() restart the process.
            except ImportError:
                print("❌ Failed to enable Rust hot-reloader (bustapi_core not found)")

    if workers is None:
        workers = 1 if debug else multiprocessing.cpu_count()

    # Server Dispatch
    if server == "rust":
        try:
            # Access protected member _rust_app usually not recommended but strict refactor
            app._rust_app.run(host, port, workers, debug)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"❌ Server error: {e}")

    elif server == "uvicorn":
        try:
            import uvicorn

            config = uvicorn.Config(
                app=app.asgi_app,
                host=host,
                port=port,
                workers=workers,
                log_level="debug" if debug else "info",
                interface="asgi3",
                **options,
            )
            server_instance = uvicorn.Server(config)
            server_instance.run()
        except ImportError:
            print("❌ 'uvicorn' not installed. Install it via `pip install uvicorn`.")
        except Exception as e:
            print(f"❌ Uvicorn error: {e}")

    elif server == "gunicorn":
        print("⚠️ Gunicorn is typically run via command line: `gunicorn module:app`")
        print(
            "   Starting Gunicorn programmatically via subprocess as a convenience..."
        )
        try:
            from gunicorn.app.base import BaseApplication

            class StandaloneApplication(BaseApplication):
                def __init__(self, app_instance, options=None):
                    self.application = app_instance
                    self.options = options or {}
                    super().__init__()

                def load_config(self):
                    config = {
                        key: value
                        for key, value in self.options.items()
                        if key in self.cfg.settings and value is not None
                    }
                    for key, value in config.items():
                        self.cfg.set(key.lower(), value)

                def load(self):
                    return self.application

            gunicorn_options = {
                "bind": f"{host}:{port}",
                "workers": workers,
                "loglevel": "debug" if debug else "info",
                **options,
            }
            StandaloneApplication(app, gunicorn_options).run()

        except ImportError:
            print("❌ 'gunicorn' not installed. Install it via `pip install gunicorn`.")
        except Exception as e:
            print(f"❌ Gunicorn error: {e}")

    elif server == "hypercorn":
        try:
            import asyncio

            from hypercorn.asyncio import serve
            from hypercorn.config import Config

            config = Config()
            config.bind = [f"{host}:{port}"]
            config.workers = workers
            config.loglevel = "debug" if debug else "info"
            asyncio.run(serve(app.asgi_app, config))

        except ImportError:
            print(
                "❌ 'hypercorn' not installed. Install it via `pip install hypercorn`."
            )
        except Exception as e:
            print(f"❌ Hypercorn error: {e}")
