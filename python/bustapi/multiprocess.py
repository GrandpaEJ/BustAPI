"""
Cross-platform multiprocessing support for BustAPI.

This module provides platform-specific socket sharing mechanisms:
- Linux: SO_REUSEPORT (kernel load balancing)
- macOS: Pre-fork with inherited file descriptor
- Windows: socket.share()/socket.fromshare() via WSADuplicateSocket
"""

import multiprocessing
import os
import platform
import signal
import socket
import sys
from typing import Optional, Tuple


class SocketManager:
    """
    Manages socket creation and sharing across worker processes.

    Platform-specific behavior:
    - Linux: Uses SO_REUSEPORT for kernel-level load balancing
    - macOS: Creates socket in parent, children inherit FD at fork
    - Windows: Uses socket.share()/fromshare() for cross-process sharing
    """

    def __init__(self, host: str, port: int, backlog: int = 1024):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.platform = platform.system()
        self._socket: Optional[socket.socket] = None
        self._shared_data: Optional[bytes] = None  # Windows only

    def create_listening_socket(self) -> socket.socket:
        """Create and bind a listening socket."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Linux: Enable SO_REUSEPORT for kernel load balancing
        if self.platform == "Linux":
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except (AttributeError, OSError):
                pass  # SO_REUSEPORT not available

        sock.bind((self.host, self.port))
        sock.listen(self.backlog)
        sock.setblocking(True)

        self._socket = sock
        return sock

    def get_socket_fd(self) -> int:
        """Get the file descriptor of the listening socket (Unix only)."""
        if self._socket is None:
            raise RuntimeError(
                "Socket not created. Call create_listening_socket() first."
            )
        return self._socket.fileno()

    def share_socket_for_child(self, child_pid: int) -> bytes:
        """
        Prepare socket for sharing with a child process (Windows only).

        Uses WSADuplicateSocket via Python's socket.share().
        """
        if self.platform != "Windows":
            raise RuntimeError("share_socket_for_child() is only for Windows")

        if self._socket is None:
            raise RuntimeError(
                "Socket not created. Call create_listening_socket() first."
            )

        return self._socket.share(child_pid)

    @staticmethod
    def recreate_socket_from_share(shared_data: bytes) -> socket.socket:
        """
        Recreate a socket from shared data (Windows only).

        Used by child processes to reconstruct the socket.
        """
        return socket.fromshare(shared_data)

    @staticmethod
    def recreate_socket_from_fd(fd: int) -> socket.socket:
        """
        Recreate a socket from a file descriptor (Unix only).

        Used by forked child processes to use the inherited FD.
        """
        return socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)

    def close(self):
        """Close the socket."""
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None


def spawn_workers_linux(rust_app, host: str, port: int, workers: int, debug: bool):
    """
    Spawn worker processes on Linux using fork + SO_REUSEPORT.

    Each child binds independently with SO_REUSEPORT.
    Kernel handles load balancing.
    """
    processes = []
    parent_pid = os.getpid()  # Track parent PID
    print(f"[BustAPI] Starting {workers} worker processes (Linux SO_REUSEPORT)...")

    def signal_handler(sig, frame):
        # Only parent should handle signals for child management
        if os.getpid() != parent_pid:
            return
        print("\n[BustAPI] Shutting down workers...")
        for p in processes:
            try:
                if p.is_alive():
                    p.terminate()
            except (AssertionError, OSError):
                pass  # Process already dead or not our child
        sys.exit(0)

    # Only register signal handlers in main thread
    try:
        import threading

        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
    except (ValueError, RuntimeError):
        pass  # Not in main thread or interpreter shutting down

    for i in range(workers):
        p = multiprocessing.Process(
            target=rust_app.run,
            args=(host, port, 1, debug),
            name=f"bustapi-worker-{i + 1}",
        )
        p.start()
        processes.append(p)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        signal_handler(None, None)


def spawn_workers_macos(rust_app, host: str, port: int, workers: int, debug: bool):
    """
    Spawn worker processes on macOS.

    macOS SO_REUSEPORT has poor load balancing.
    For now, fallback to single process mode.
    """
    # macOS multiprocessing is complex without SO_REUSEPORT - fallback to single process
    print("[BustAPI] Starting server on macOS (single process mode)...")
    print("[BustAPI] Note: Multi-worker mode requires SO_REUSEPORT (Linux only)")
    rust_app.run(host, port, workers, debug)


def spawn_workers_windows(rust_app, host: str, port: int, workers: int, debug: bool):
    """
    Spawn worker processes on Windows.

    Windows doesn't support SO_REUSEPORT, so we spawn independent workers.
    Only the first worker will successfully bind; others will fail.
    For now, fallback to single worker on Windows.
    """
    # Windows multiprocessing is complex - fallback to single process
    print("[BustAPI] Starting server on Windows (single process mode)...")
    print("[BustAPI] Note: Multi-worker mode requires SO_REUSEPORT (Linux only)")
    rust_app.run(host, port, workers, debug)


def spawn_workers(rust_app, host: str, port: int, workers: int, debug: bool):
    """
    Spawn worker processes using the best method for the current platform.
    """
    system = platform.system()

    if system == "Linux":
        spawn_workers_linux(rust_app, host, port, workers, debug)
    elif system == "Darwin":  # macOS
        spawn_workers_macos(rust_app, host, port, workers, debug)
    elif system == "Windows":
        spawn_workers_windows(rust_app, host, port, workers, debug)
    else:
        # Unknown platform, fallback to single process
        print(f"⚠️ Unknown platform: {system}. Running single process.")
        rust_app.run(host, port, workers, debug)
