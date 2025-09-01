#!/usr/bin/env python3
"""Simple benchmark runner to compare BustAPI, Flask and FastAPI hello endpoints.

Usage:
  python benchmarks/run_bench.py --target all --concurrency 100 --duration 10

This script will start each server in a subprocess, run a simple async load test using httpx,
then kill the server and report requests/sec.

Notes:
- Requires `httpx` and `uvicorn`/`fastapi`/`flask` installed in the environment.
- It's intentionally minimal; use a proper load generator (wrk, vegeta) for production-grade results.
"""

import argparse
import asyncio
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
APPS = {
    "bustapi": {
        "cmd": [sys.executable, str(ROOT / "apps" / "bustapi_app.py")],
        "url": "http://127.0.0.1:8001/hello",
    },
    "flask": {
        "cmd": [sys.executable, str(ROOT / "apps" / "flask_app.py")],
        "url": "http://127.0.0.1:8002/hello",
    },
    "fastapi": {
        "cmd": [sys.executable, str(ROOT / "apps" / "fastapi_app.py")],
        "url": "http://127.0.0.1:8003/hello",
    },
}


async def worker_request_limited(
    task_id: int,
    client: httpx.AsyncClient,
    url: str,
    target_requests: int,
    counter,
    stop_event: asyncio.Event,
):
    while not stop_event.is_set():
        try:
            r = await client.get(url, timeout=10.0)
            if r.status_code == 200:
                counter[0] += 1
            else:
                counter[1] += 1
        except Exception:
            counter[1] += 1

        # check if we've reached target
        if counter[0] + counter[1] >= target_requests:
            stop_event.set()
            break


async def run_load_duration(url: str, concurrency: int, duration: int):
    counter = [0, 0]
    async with httpx.AsyncClient() as client:
        stop_time = time.time() + duration
        tasks = [
            asyncio.create_task(
                worker_request_limited(i, client, url, 10**9, counter, asyncio.Event())
            )
            for i in range(concurrency)
        ]
        # reuse the same event and a large target to emulate duration-based run
        await asyncio.gather(*tasks)
    return counter


async def run_load_requests(url: str, concurrency: int, target_requests: int):
    counter = [0, 0]
    stop_event = asyncio.Event()
    async with httpx.AsyncClient() as client:
        tasks = [
            asyncio.create_task(
                worker_request_limited(
                    i, client, url, target_requests, counter, stop_event
                )
            )
            for i in range(concurrency)
        ]
        await stop_event.wait()
        # wait a moment for tasks to observe stop
        await asyncio.gather(*tasks, return_exceptions=True)
    return counter


def run_server(cmd):
    return subprocess.Popen(cmd)


def run_target_requests(target: str, concurrency: int, target_requests: int):
    app = APPS[target]
    print(f"Starting {target} server: {' '.join(app['cmd'])}")
    proc = run_server(app["cmd"])
    try:
        time.sleep(1.5)  # wait for startup (adjust if needed)
        print(
            f"Running load: {concurrency} concurrency for {target_requests} total requests against {app['url']}"
        )
        start = time.time()
        results = asyncio.run(
            run_load_requests(app["url"], concurrency, target_requests)
        )
        elapsed = time.time() - start
        success, errors = results
        rps = success / elapsed if elapsed > 0 else 0.0
        print(
            f"{target} results: success={success}, errors={errors}, elapsed={elapsed:.2f}s, rps={rps:.2f}"
        )
        return {
            "target": target,
            "success": success,
            "errors": errors,
            "elapsed": elapsed,
            "rps": rps,
            "concurrency": concurrency,
        }
    finally:
        proc.terminate()
        try:
            proc.wait(3)
        except Exception:
            proc.kill()


def run_target_duration(target: str, concurrency: int, duration: int):
    # keep compatibility with duration-based runs
    app = APPS[target]
    print(f"Starting {target} server: {' '.join(app['cmd'])}")
    proc = run_server(app["cmd"])
    try:
        time.sleep(1.5)
        print(
            f"Running load: {concurrency} concurrency for {duration}s against {app['url']}"
        )
        start = time.time()
        results = asyncio.run(run_load_requests(app["url"], concurrency, 10**9))
        elapsed = time.time() - start
        success, errors = results
        rps = success / duration if duration > 0 else 0.0
        print(
            f"{target} results: success={success}, errors={errors}, elapsed={elapsed:.2f}s, rps={rps:.2f}"
        )
        return {
            "target": target,
            "success": success,
            "errors": errors,
            "elapsed": elapsed,
            "rps": rps,
            "concurrency": concurrency,
        }
    finally:
        proc.terminate()
        try:
            proc.wait(3)
        except Exception:
            proc.kill()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target", default="all", choices=["all", "bustapi", "flask", "fastapi"]
    )
    parser.add_argument("--concurrency", type=int, default=50)
    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="duration in seconds (mutually exclusive with --requests)",
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=None,
        help="total number of requests to send (mutually exclusive with --duration)",
    )
    args = parser.parse_args()

    targets = [args.target] if args.target != "all" else ["bustapi", "flask", "fastapi"]
    results = []
    for t in targets:
        if args.requests is not None:
            res = run_target_requests(t, args.concurrency, args.requests)
            results.append(res)
        else:
            dur = args.duration if args.duration is not None else 10
            res = run_target_duration(t, args.concurrency, dur)
            results.append(res)

    # write a simple results file for quick inspection
    out = Path(__file__).parent / "last_results.txt"
    with out.open("w") as fh:
        for r in results:
            fh.write(f"{r}\n")
    print(f"Wrote results to {out}")


if __name__ == "__main__":
    main()
