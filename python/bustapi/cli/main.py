#!/usr/bin/env python3
"""
BustAPI CLI - Command line interface for BustAPI framework.

Usage:
    bustapi new <name> [--uv|--poetry]   Create new project
    bustapi run [file]                   Run development server
    bustapi routes                       List all routes
    bustapi --version                    Show version
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from .. import __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="bustapi",
        description="BustAPI - High-performance Flask-compatible web framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bustapi new myapp              Create new project with pip
  bustapi new myapp --uv         Create new project with uv
  bustapi new myapp --poetry     Create new project with poetry
  bustapi run                    Run app.py or main.py
  bustapi run server.py          Run specific file
  bustapi routes                 List all registered routes
        """,
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"BustAPI {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # bustapi new
    new_parser = subparsers.add_parser("new", help="Create a new BustAPI project")
    new_parser.add_argument("name", help="Project name")
    new_parser.add_argument("--uv", action="store_true", help="Use uv package manager")
    new_parser.add_argument(
        "--poetry", action="store_true", help="Use poetry package manager"
    )

    # bustapi run
    run_parser = subparsers.add_parser("run", help="Run development server")
    run_parser.add_argument(
        "file", nargs="?", default=None, help="Python file to run (default: app.py)"
    )
    run_parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)"
    )
    run_parser.add_argument(
        "--port", "-p", type=int, default=5000, help="Port to bind (default: 5000)"
    )
    run_parser.add_argument(
        "--reload", "-r", action="store_true", help="Enable hot reload"
    )

    # bustapi routes
    subparsers.add_parser("routes", help="List all registered routes")

    # bustapi info
    subparsers.add_parser("info", help="Show BustAPI installation info")

    args = parser.parse_args()

    if args.command == "new":
        cmd_new(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "routes":
        cmd_routes(args)
    elif args.command == "info":
        cmd_info(args)
    else:
        parser.print_help()


def cmd_new(args):
    """Create a new BustAPI project."""
    project_name = args.name
    project_path = Path(project_name)

    # Handle "." for current directory
    if project_name == ".":
        project_path = Path.cwd()
        project_name = project_path.name
        # Check if directory already has files (except hidden)
        existing_files = [
            f for f in project_path.iterdir() if not f.name.startswith(".")
        ]
        if existing_files and not any(
            f.name in ["main.py", "app.py"] for f in existing_files
        ):
            # Allow if empty or only hidden files
            pass
    else:
        if project_path.exists():
            print(f"❌ Error: Directory '{project_name}' already exists")
            sys.exit(1)
        # Create the directory
        project_path.mkdir(parents=True)

    print(f"🚀 Creating new BustAPI project: {project_name}")

    # Create directories (ignore if exist)
    (project_path / "templates").mkdir(exist_ok=True)
    (project_path / "static").mkdir(exist_ok=True)
    (project_path / "static" / "css").mkdir(exist_ok=True)
    (project_path / "static" / "js").mkdir(exist_ok=True)

    # Create main.py
    main_py = '''"""
{name} - Built with BustAPI
"""

from bustapi import BustAPI, render_template

app = BustAPI(__name__)
app.secret_key = "change-this-in-production"


@app.route("/")
def index():
    return render_template("index.html", title="Welcome to {name}")


@app.route("/api/hello")
def api_hello():
    return {{"message": "Hello from BustAPI!", "status": "ok"}}


if __name__ == "__main__":
    app.run(debug=True)
'''.format(name=project_name)

    (project_path / "main.py").write_text(main_py)

    # Create templates/index.html
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <h1>🚀 {{ title }}</h1>
        <p>Your BustAPI app is running!</p>
        <div class="links">
            <a href="/api/hello">API Endpoint</a>
        </div>
    </div>
</body>
</html>
"""
    (project_path / "templates" / "index.html").write_text(index_html)

    # Create static/css/style.css
    style_css = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.container {
    background: white;
    padding: 3rem;
    border-radius: 1rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    text-align: center;
    max-width: 500px;
}

h1 {
    color: #333;
    margin-bottom: 1rem;
}

p {
    color: #666;
    margin-bottom: 2rem;
}

.links a {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background: #667eea;
    color: white;
    text-decoration: none;
    border-radius: 0.5rem;
    transition: transform 0.2s;
}

.links a:hover {
    transform: translateY(-2px);
}
"""
    (project_path / "static" / "css" / "style.css").write_text(style_css)

    # Create dependency file based on package manager
    if args.uv or args.poetry:
        pyproject = f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "A BustAPI application"
requires-python = ">=3.10"
dependencies = [
    "bustapi>={__version__}",
]

[project.scripts]
dev = "python main.py"
"""
        if args.poetry:
            pyproject = f"""[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = "A BustAPI application"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"
bustapi = "^{__version__}"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
        (project_path / "pyproject.toml").write_text(pyproject)
    else:
        requirements = f"bustapi>={__version__}\n"
        (project_path / "requirements.txt").write_text(requirements)

    # Create .gitignore
    gitignore = """__pycache__/
*.py[cod]
*$py.class
.env
.venv/
venv/
*.egg-info/
dist/
build/
.pytest_cache/
"""
    (project_path / ".gitignore").write_text(gitignore)

    print(f"✅ Created project: {project_name}/")
    print()
    print("📁 Project structure:")
    print(f"   {project_name}/")
    print("   ├── main.py")
    print("   ├── templates/")
    print("   │   └── index.html")
    print("   ├── static/")
    print("   │   └── css/style.css")
    if args.uv or args.poetry:
        print("   └── pyproject.toml")
    else:
        print("   └── requirements.txt")
    print()
    print("🎉 Get started:")
    if args.name != ".":
        print(f"   cd {project_name}")
    if args.uv:
        print("   uv sync")
        print("   uv run python main.py")
    elif args.poetry:
        print("   poetry install")
        print("   poetry run python main.py")
    else:
        print("   pip install -r requirements.txt")
        print("   python main.py")


def cmd_run(args):
    """Run the development server."""
    # Find the app file
    if args.file:
        app_file = Path(args.file)
    else:
        # Auto-detect
        candidates = ["app.py", "main.py", "server.py", "run.py"]
        app_file = None
        for candidate in candidates:
            if Path(candidate).exists():
                app_file = Path(candidate)
                break

        if not app_file:
            print("❌ Error: No app file found. Tried: " + ", ".join(candidates))
            print("   Specify a file: bustapi run myapp.py")
            sys.exit(1)

    if not app_file.exists():
        print(f"❌ Error: File '{app_file}' not found")
        sys.exit(1)

    print(f"🚀 Running {app_file} on http://{args.host}:{args.port}")
    print("   Press Ctrl+C to stop")
    print()

    # Set environment variables
    env = os.environ.copy()
    env["BUSTAPI_HOST"] = args.host
    env["BUSTAPI_PORT"] = str(args.port)
    if args.reload:
        env["BUSTAPI_RELOAD"] = "1"

    try:
        subprocess.run([sys.executable, str(app_file)], env=env)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


def cmd_routes(args):
    """List all registered routes."""
    # Try to import and inspect the app
    candidates = ["app.py", "main.py", "server.py"]
    app_file = None
    for candidate in candidates:
        if Path(candidate).exists():
            app_file = candidate
            break

    if not app_file:
        print("❌ No app file found to inspect routes")
        sys.exit(1)

    print(f"📋 Routes from {app_file}:")
    print()

    # Import the module
    import importlib.util

    spec = importlib.util.spec_from_file_location("app_module", app_file)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)

            # Find BustAPI app instance
            app = None
            for name in dir(module):
                obj = getattr(module, name)
                if hasattr(obj, "_routes") or hasattr(obj, "url_map"):
                    app = obj
                    break

            if app and hasattr(app, "_routes"):
                print(f"{'Method':<10} {'Path':<30} {'Handler':<20}")
                print("-" * 60)
                for route in app._routes:
                    method = route.get("methods", ["GET"])[0]
                    path = route.get("path", "/")
                    handler = route.get("handler", lambda: None).__name__
                    print(f"{method:<10} {path:<30} {handler:<20}")
            else:
                print("No routes found or app not detected")
        except Exception as e:
            print(f"Error loading app: {e}")


def cmd_info(args):
    """Show BustAPI installation info."""
    import platform

    print("🔧 BustAPI Info")
    print("-" * 40)
    print(f"  Version:        {__version__}")
    print(f"  Python:         {platform.python_version()}")
    print(f"  Platform:       {platform.system()} {platform.release()}")
    print(f"  Architecture:   {platform.machine()}")

    try:
        from .. import bustapi_core

        print("  Rust Core:      ✅ Loaded")
    except ImportError:
        print("  Rust Core:      ❌ Not available")


if __name__ == "__main__":
    main()
