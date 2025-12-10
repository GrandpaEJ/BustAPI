# Installation

## Prerequisites

- **Python**: 3.10 or higher.
- **Operating System**: Linux, macOS, or Windows (WSL recommended).

> [!NOTE]
> For best performance, use **Python 3.13t** (free-threaded build) to enable true parallelism. BustAPI automatically detects and utilizes the free-threaded mode.

## Install via Pip

BustAPI is available on PyPI and can be installed via pip:

```bash
pip install bustapi
```

This installs the pre-compiled binary wheel for your platform. No Rust toolchain is required for installation.

## Verifying Installation

To verify that BustAPI is installed correctly, you can check the version:

```bash
python -c "import bustapi; print(bustapi.__version__)"
```

You should see `0.3.0` (or later) printed to the console.

## For Contributors (Building from Source)

If you want to contribute to BustAPI or build from source, you will need the Rust toolchain installed.

1.  **Install Rust**: https://rustup.rs/
2.  **Clone the Repository**:
    ```bash
    git clone https://github.com/GrandpaEJ/bustapi.git
    cd bustapi
    ```
3.  **Install Dependencies**:
    ```bash
    pip install .[dev]
    ```
4.  **Build**:
    ```bash
    maturin develop
    ```
