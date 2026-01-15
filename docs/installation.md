# :package: Installation

Get BustAPI up and running in seconds.

---

## :zap: Quick Install

=== ":material-language-python: pip"

    ```bash
    pip install bustapi
    ```

=== ":material-package: uv (faster)"

    ```bash
    uv pip install bustapi
    ```

=== ":material-package-variant: pipx (isolated)"

    ```bash
    pipx install bustapi
    ```

!!! success "That's it!"
    Pre-built wheels are available. No Rust toolchain required.

---

## :white_check_mark: Requirements

| Requirement | Versions |
|:------------|:---------|
| **Python** | 3.10, 3.11, 3.12, 3.13, 3.14 |
| **OS** | Linux, macOS, Windows |
| **Architecture** | x86_64, arm64 (Apple Silicon) |

---

## :globe_with_meridians: Platform Support

<div class="grid cards" markdown>

-   :fontawesome-brands-linux:{ .lg .middle } **Linux (Recommended)**

    ---

    **Best performance** with native multiprocessing.
    
    - :material-check: 100,000+ RPS with 4 workers
    - :material-check: `SO_REUSEPORT` kernel load balancing
    - :material-check: Optimal for production

-   :fontawesome-brands-apple:{ .lg .middle } **macOS**

    ---

    **Fully supported** for development.
    
    - :material-check: ~35,000 RPS (single-process)
    - :material-check: Apple Silicon native
    - :material-check: Great for local development

-   :fontawesome-brands-windows:{ .lg .middle } **Windows**

    ---

    **Fully supported** for development.
    
    - :material-check: ~17,000 RPS (single-process)
    - :material-check: x64 pre-built wheels
    - :material-check: Great for local development

</div>

!!! warning "Production Recommendation"
    For maximum performance, **deploy on Linux servers**.  
    macOS and Windows are ideal for development.

---

## :hammer_and_wrench: Development Install

To build from source (requires Rust):

=== ":fontawesome-brands-linux: Linux / macOS"

    ```bash
    # Install Rust
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    
    # Clone and build
    git clone https://github.com/GrandpaEJ/BustAPI.git
    cd BustAPI
    pip install maturin
    maturin develop --release
    ```

=== ":fontawesome-brands-windows: Windows"

    ```powershell
    # Install Rust from https://rustup.rs
    
    # Clone and build
    git clone https://github.com/GrandpaEJ/BustAPI.git
    cd BustAPI
    pip install maturin
    maturin develop --release
    ```

---

## :white_check_mark: Verify Installation

```python
>>> import bustapi
>>> print(bustapi.__version__)
0.8.0
```

---

## :rocket: Next Steps

Ready to build something? Check out the [Quickstart Guide](quickstart.md)!
