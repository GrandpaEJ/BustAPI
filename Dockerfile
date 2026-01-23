FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
# We keep build-essential and add cargo/rust for compiling BustAPI's Rust core
# can be ignored if you're not using the Rust extension
# but build-essential needed for libc 
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    curl \
    cargo \
    pkg-config \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies and the package itself
# This builds the Rust extension (requires cargo)
RUN pip3 install --no-cache-dir . --break-system-packages

# Default command
CMD ["python3", "app.py"]
