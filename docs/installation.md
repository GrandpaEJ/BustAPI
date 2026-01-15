# Installation

## Quick Install

```bash
pip install bustapi
```

**Supported Python versions:** 3.10, 3.11, 3.12, 3.13, 3.14

Pre-built wheels are available for:

- 🐧 **Linux** (x86_64, aarch64)
- 🍎 **macOS** (x86_64, arm64)
- 🪟 **Windows** (x86_64)

---

## Platform Recommendations

### 🐧 Linux (Recommended for Production)

Linux provides the **best performance** with native multiprocessing:

- **100,000+ RPS** with 4 workers
- Kernel-level load balancing via `SO_REUSEPORT`
- Optimal for production deployments

```bash
pip install bustapi
python app.py  # Automatically uses multiprocessing
```

### 🍎 macOS (Development)

Fully supported for development. Runs in single-process mode (~35k RPS):

```bash
pip install bustapi
python app.py
```

### 🪟 Windows (Development)

Fully supported for development. Runs in single-process mode (~17k RPS):

```bash
pip install bustapi
python app.py
```

> ⚠️ **Production Recommendation:** For maximum performance, deploy on **Linux servers**. macOS and Windows are ideal for development but lack the multiprocessing optimizations available on Linux.

---

## Development Install (From Source)

To build from source, you'll need Rust installed:

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Clone and build
git clone https://github.com/GrandpaEJ/BustAPI.git
cd BustAPI
pip install maturin
maturin develop --release
```

---

## Verify Installation

```python
import bustapi
print(bustapi.__version__)  # Should print 0.8.0
```

## Next Steps

- [Quickstart Guide](quickstart.md)
- [Routing Guide](user-guide/routing.md)
