import glob
import os
import re
import signal
import subprocess
import sys
import time

import httpx


def find_port(content):
    match = re.search(r"port=(\d+)", content)
    if match:
        return int(match.group(1))
    return 5000


def find_routes(content):
    # Matches @app.route("/path") or @app.route("/path", methods=...)
    return re.findall(r'@app\.route\("([^"]+)"', content)


def get_test_url(route):
    # Replace path parameters with dummy values
    route = re.sub(r"<int:[^>]+>", "1", route)
    route = re.sub(r"<str:[^>]+>", "test", route)
    route = re.sub(r"<path:[^>]+>", "path/to/resource", route)
    route = re.sub(r"<[^>]+>", "1", route)  # Generic fallback
    return route


def main():
    examples_dir = os.path.join(os.getcwd(), "examples")
    files = sorted(glob.glob(os.path.join(examples_dir, "*.py")))

    print(f"Found {len(files)} files in {examples_dir}")

    for file_path in files:
        filename = os.path.basename(file_path)
        if filename == "__init__.py" or filename.startswith("__"):
            continue

        print(f"\n{'=' * 50}")
        print(f"Processing {filename}")

        with open(file_path, "r") as f:
            content = f.read()

        routes = find_routes(content)
        if not routes:
            print(f"No routes found in {filename}, skipping.")
            continue

        port = find_port(content)
        print(f"Found port: {port}")
        print(f"Found routes: {routes}")

        # Determine args
        args = ["uv", "run", file_path]
        if filename == "12_test_modes.py":
            args.append("rust")

        # Start the process
        print(f"Starting {filename} with args {args}...")
        process = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        try:
            # Wait for server to start
            time.sleep(3)

            # Check if process is still running
            if process.poll() is not None:
                print(f"Process exited early. Stderr: {process.stderr.read()}")
                continue

            # Test endpoints
            for route in routes:
                test_path = get_test_url(route)
                url = f"http://127.0.0.1:{port}{test_path}"
                print(f"Testing {url}...")

                # Test 2 times
                for i in range(2):
                    try:
                        response = httpx.get(url, timeout=5)
                        print(f"  Attempt {i + 1}: Status {response.status_code}")
                    except Exception as e:
                        print(f"  Attempt {i + 1}: Failed - {e}")

        except Exception as e:
            print(f"Error running {filename}: {e}")

        finally:
            print("Stopping server...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            print("Stopped.")
            time.sleep(1)  # Cooldown


if __name__ == "__main__":
    main()
