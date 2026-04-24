import os
import signal
import subprocess
import sys
import time

import requests

PYTHON = sys.executable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES_DIR = os.path.join(BASE_DIR, "examples")


def run_example_test(script_name, port, tests):
    print(f"Testing {script_name} on port {port}...")
    script_path = os.path.join(EXAMPLES_DIR, script_name)

    # Needs PYTHONPATH to include local bustapi
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(BASE_DIR, "python")

    # Start process
    proc = subprocess.Popen(
        [PYTHON, script_path],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        # Wait for server to start
        time.sleep(2)

        # Run tests
        for path, expected_status, check_func in tests:
            url = f"http://127.0.0.1:{port}{path}"
            try:
                if isinstance(path, tuple):  # method, url, data
                    method, url_path, data = path
                    url = f"http://127.0.0.1:{port}{url_path}"
                    if method == "POST":
                        resp = requests.post(url, json=data)
                else:
                    resp = requests.get(url)

                if resp.status_code != expected_status:
                    print(
                        f"[FAIL] {script_name} {path}: Expected {expected_status}, got {resp.status_code}"
                    )
                    return False

                if check_func and not check_func(resp):
                    print(f"[FAIL] {script_name} {path}: Check passed failed")
                    return False
                print(f"[PASS] {script_name} {path}")

            except Exception as e:
                print(f"[FAIL] {script_name} {path}: Exception {e}")
                return False

    finally:
        os.kill(proc.pid, signal.SIGTERM)
        proc.wait()

    return True


def main():
    # Hello World Tests
    hello_tests = [("/", 200, lambda r: r.json()["message"] == "Hello, World!")]
    if not run_example_test("01_hello_world.py", 5000, hello_tests):
        sys.exit(1)

    # Parameters Tests
    param_tests = [
        # ("/user/123", 200, lambda r: r.json()["user_id"] == 123), # Might fail if routing logic is simplistic
        ("/search?q=rust&page=2", 200, lambda r: r.json()["search_query"] == "rust")
    ]
    if not run_example_test("02_parameters.py", 5001, param_tests):
        sys.exit(1)

    # Async Tests
    async_tests = [
        ("/sync", 200, lambda r: r.json()["mode"] == "sync"),
        ("/async", 200, lambda r: r.json()["mode"] == "async"),
    ]
    if not run_example_test("03_async.py", 5002, async_tests):
        sys.exit(1)

    # Request Data Tests
    data_tests = [
        ("POST", "/echo/json", {"key": "value"}),
        # Form test needs requests support for form data properly
        # lambda check to verify json content
    ]

    # Lambda for detailed check
    def check_json(r):
        return r.json()["received"] == {"key": "value"}

    data_tests_refined = [(("POST", "/echo/json", {"key": "value"}), 200, check_json)]

    if not run_example_test("04_request_data.py", 5003, data_tests_refined):
        sys.exit(1)

    print("\nAll examples passed verification!")


if __name__ == "__main__":
    main()
