"""
WebSocket Benchmark for BustAPI

Measures:
- Connection time
- Round-trip latency
- Messages per second

Usage:
    python ws_benchmark.py [port]
"""

import asyncio
import statistics
import sys
import time

import websockets

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8005
WS_URL = (
    f"ws://127.0.0.1:{PORT}/ws" if PORT == 8005 else f"ws://127.0.0.1:{PORT}/ws/turbo"
)
NUM_MESSAGES = 1000
NUM_CONNECTIONS = 10


async def benchmark_single_connection():
    """Benchmark a single connection with many messages."""
    latencies = []

    async with websockets.connect(WS_URL) as ws:
        # Note: Server doesn't send welcome message, go straight to benchmarking

        start_total = time.perf_counter()

        for i in range(NUM_MESSAGES):
            msg = f"Benchmark message {i}"
            start = time.perf_counter()
            await ws.send(msg)
            response = await ws.recv()
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # ms

        end_total = time.perf_counter()

    return {
        "total_time": end_total - start_total,
        "latencies": latencies,
        "messages": NUM_MESSAGES,
    }


async def benchmark_concurrent_connections():
    """Benchmark multiple concurrent connections."""

    async def single_client(client_id):
        latencies = []
        async with websockets.connect(WS_URL) as ws:
            # No welcome message to discard

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


async def main():
    print("=" * 60)
    print("BustAPI WebSocket Benchmark")
    print("=" * 60)

    print(f"\n1. Single Connection Benchmark ({NUM_MESSAGES} messages)...")
    result = await benchmark_single_connection()

    avg_lat = statistics.mean(result["latencies"])
    p50 = statistics.median(result["latencies"])
    p99 = sorted(result["latencies"])[int(len(result["latencies"]) * 0.99)]
    msgs_per_sec = result["messages"] / result["total_time"]

    print(f"   Total Time: {result['total_time']:.2f}s")
    print(f"   Messages/sec: {msgs_per_sec:,.0f}")
    print(f"   Avg Latency: {avg_lat:.3f}ms")
    print(f"   P50 Latency: {p50:.3f}ms")
    print(f"   P99 Latency: {p99:.3f}ms")

    print(
        f"\n2. Concurrent Connections Benchmark ({NUM_CONNECTIONS} clients, {NUM_MESSAGES} total messages)..."
    )
    result = await benchmark_concurrent_connections()

    avg_lat = statistics.mean(result["latencies"])
    p50 = statistics.median(result["latencies"])
    p99 = sorted(result["latencies"])[int(len(result["latencies"]) * 0.99)]
    msgs_per_sec = result["messages"] / result["total_time"]

    print(f"   Total Time: {result['total_time']:.2f}s")
    print(f"   Messages/sec: {msgs_per_sec:,.0f}")
    print(f"   Avg Latency: {avg_lat:.3f}ms")
    print(f"   P50 Latency: {p50:.3f}ms")
    print(f"   P99 Latency: {p99:.3f}ms")

    print("\n" + "=" * 60)
    print("Benchmark Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
