# CLI Tool

BustAPI includes a powerful command-line interface (CLI) to help you scaffold new projects, run development servers, and inspect your application.

## Installation

The CLI is installed automatically with `pip install bustapi`.

## Commands

### `new` - Create Project

Scaffold a new BustAPI project with best practices.

```bash
bustapi new <project_name> [options]
```

**Options:**

- `--uv`: Initialize project with `uv` package manager (creates `pyproject.toml`).
- `--poetry`: Initialize project with `poetry` package manager (creates `pyproject.toml`).
- Default (no flag): Uses `pip` and creates `requirements.txt`.

**Example:**
```bash
bustapi new my-api --uv
cd my-api
uv sync
```

### `run` - Development Server

Run the development server with hot-reloading enabled.

```bash
bustapi run [file]
```

- **file**: Path to your application file (default: `main.py` or `app.py`).

**Features:**
- Native Rust hot-reloading (extremely fast).
- Automatic discovery of app entry point.

### `routes` - List Routes

Inspect all registered routes in your application.

```bash
bustapi routes [file]
```

### `info` - System Info

Display system information and debugging details.

```bash
bustapi info
```
