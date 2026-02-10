"""
Server runner logic for BustAPI.
"""

import multiprocessing
import os
import sys
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import BustAPI


def run_server_rust(
    app: "BustAPI",
    host: str,
    port: int,
    workers: int,
    debug: bool,
    verbose: bool = False,
):
    """Run the native Rust HTTP server."""
    if workers > 1 and not debug:
        from ..multiprocess import spawn_workers

        spawn_workers(app._rust_app, host, port, workers, debug, verbose)
        return

    try:
        app._rust_app.run(host, port, workers, debug, verbose, workers)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ Server error: {e}")


def run_server_uvicorn(
    app: "BustAPI", host: str, port: int, workers: int, debug: bool, **options
):
    """Run with Uvicorn ASGI server."""
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
        server = uvicorn.Server(config)
        server.run()
    except ImportError:
        print("❌ 'uvicorn' not installed. Install via `pip install uvicorn`.")
    except Exception as e:
        print(f"❌ Uvicorn error: {e}")


def run_server_gunicorn(
    app: "BustAPI", host: str, port: int, workers: int, debug: bool, **options
):
    """Run with Gunicorn WSGI server."""
    try:
        from gunicorn.app.base import BaseApplication

        class StandaloneApplication(BaseApplication):
            def __init__(self, app, opts=None):
                self.application = app
                self.options = opts or {}
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
        print("❌ 'gunicorn' not installed. Install via `pip install gunicorn`.")
    except Exception as e:
        print(f"❌ Gunicorn error: {e}")


def run_server_hypercorn(
    app: "BustAPI", host: str, port: int, workers: int, debug: bool, **options
):
    """Run with Hypercorn ASGI server."""
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
        print("❌ 'hypercorn' not installed. Install via `pip install hypercorn`.")
    except Exception as e:
        print(f"❌ Hypercorn error: {e}")


def enable_hot_reload():
    """Enable Rust-native hot reload."""
    if os.environ.get("BUSTAPI_RELOADER_RUN") != "true":
        try:
            from .. import bustapi_core

            bustapi_core.enable_hot_reload(".")
        except ImportError:
            print("⚠️ Native hot reload not available in this build.")
        except Exception as e:
            print(f"⚠️ Failed to enable hot reload: {e}")


def setup_debug_logging(app: "BustAPI"):
    """Setup request logging for debug mode."""

    def _debug_start_timer():
        try:
            import time
            from .. import request

            request.start_time = time.time()
        except ImportError:
            pass

    def _debug_log_request(response):
        try:
            import time
            from .. import logging, request

            start_time = getattr(request, "start_time", time.time())
            duration = time.time() - start_time
            logging.log_request(
                request.method, request.path, response.status_code, duration
            )
        except ImportError:
            pass
        return response

    app.before_request(_debug_start_timer)
    app.after_request(_debug_log_request)
