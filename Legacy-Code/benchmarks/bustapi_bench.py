"""
BustAPI Solo Benchmark Tool
Usage:
    python bustapi_bench.py [port]         (Runs automated benchmark)
    python bustapi_bench.py server [port]  (Runs server only)

Measures:
- Connection time
- Round-trip latency
- Messages per second
"""

import asyncio
import multiprocessing
import os
import signal
import statistics
import sys
import time

# Client Imports
try:
    import websockets
except ImportError:
    pass

# Server Imports
try:
    from bustapi import BustAPI, WebSocketHandler
except ImportError:
    pass

PORT = 8005


# --- Server Code ---
class EchoHandler:
    def on_connect(self, session_id):
        pass

    def on_message(self, session_id, message):
        return message

    def on_disconnect(self, session_id, reason):
        pass


def run_server(port):
    app = BustAPI()
    app.add_websocket_route("/ws", EchoHandler())
    app.add_turbo_websocket_route("/ws/turbo", "Echo: ")  # Baseline
    print(f"[Server] Starting on port {port}...")
    # Redirect stdout to avoid clutter
    sys.stdout = open(os.devnull, "w")
    app.run(port=port)


# --- Client Code ---
NUM_MESSAGES = 1000
NUM_CONNECTIONS = 10


async def benchmark_single_connection(url):
    latencies = []
    async with websockets.connect(url) as ws:
        start_total = time.perf_counter()
        for i in range(NUM_MESSAGES):
            msg = f"Benchmark message {i}"
            start = time.perf_counter()
            await ws.send(msg)
            response = await ws.recv()
            end = time.perf_counter()
            latencies.append((end - start) * 1000)
        end_total = time.perf_counter()
    return {
        "total_time": end_total - start_total,
        "latencies": latencies,
        "messages": NUM_MESSAGES,
    }


async def benchmark_concurrent_connections(url):
    async def single_client(client_id):
        latencies = []
        async with websockets.connect(url) as ws:
            for i in range(NUM_MESSAGES // NUM_CONNECTIONS):
                msg = f"Client {client_id} msg {i}"
                start = time.perf_counter()
                await ws.send(msg)
                await ws.recv()
                end = time.perf_counter()
                latencies.append((end - start) * 1000)
        return latencies

    start = time.perf_counter()
    tasks = [single_client(i) for i in range(NUM_CONNECTIONS)]
    results = await asyncio.gather(*tasks)
    end = time.perf_counter()
    all_latencies = [lat for r in results for lat in r]
    return {
        "total_time": end - start,
        "latencies": all_latencies,
        "connections": NUM_CONNECTIONS,
        "messages": NUM_MESSAGES,
    }


async def run_client(port):
    print("=" * 60)
    print("BustAPI WebSocket Benchmark")
    print("=" * 60)

    # Check Turbo vs Standard
    # Defaulting to Turbo for "Solo" demo usually, but let's test BOTH?
    # Or just test Turbo as it's the flagship.
    # Let's test Turbo.
    url = f"ws://127.0.0.1:{port}/ws/turbo"
    print(f"Target: {url}")

    # 1. Single
    print(f"\n1. Single Connection ({NUM_MESSAGES} msgs)...")
    res = await benchmark_single_connection(url)
    print_results(res)

    # 2. Concurrent
    print(f"\n2. Concurrent ({NUM_CONNECTIONS} clients)...")
    res = await benchmark_concurrent_connections(url)
    print_results(res)


def print_results(result):
    avg = statistics.mean(result["latencies"])
    p99 = sorted(result["latencies"])[int(len(result["latencies"]) * 0.99)]
    rps = result["messages"] / result["total_time"]
    print(f"   RPS: {rps:,.0f}")
    print(f"   Avg Latency: {avg:.3f}ms")
    print(f"   P99 Latency: {p99:.3f}ms")


# --- Main Entry ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        run_server(int(sys.argv[2]))
        sys.exit(0)

    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8005

    # Start Server Process
    server_process = multiprocessing.Process(target=run_server, args=(port,))
    server_process.start()

    time.sleep(2)  # Warmup

    try:
        if "websockets" not in sys.modules:
            import websockets

        asyncio.run(run_client(port))
    except ImportError:
        print("Error: 'websockets' library required for client.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_process.terminate()
        server_process.join()
