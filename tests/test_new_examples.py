import os
import signal
import subprocess
import sys
import time
import unittest

import requests

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PYTHON_PATH = os.path.join(PROJECT_ROOT, "python")

env = os.environ.copy()
env["PYTHONPATH"] = PYTHON_PATH


class TestNewExamples(unittest.TestCase):
    def run_example(self, script, port):
        cmd = [sys.executable, f"examples/{script}"]
        # Windows doesn't support preexec_fn/setsid
        kwargs = {
            "cwd": PROJECT_ROOT,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "env": env,
        }
        if sys.platform != "win32":
            kwargs["preexec_fn"] = os.setsid
        proc = subprocess.Popen(cmd, **kwargs)
        time.sleep(6)  # Wait for startup (6s for multiprocess apps in CI)
        if proc.poll() is not None:
            out, err = proc.communicate()
            print(f"Process failed to start! Return code: {proc.returncode}")
            print(f"STDOUT: {out.decode()}")
            print(f"STDERR: {err.decode()}")
        return proc

    def kill_process(self, proc):
        """Kill process in a cross-platform way."""
        try:
            if sys.platform == "win32":
                proc.terminate()
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except (ProcessLookupError, OSError):
            pass

    def request_with_retry(self, url, method="get", retries=3, delay=1):
        """Make HTTP request with retries for CI stability."""
        for attempt in range(retries):
            try:
                return getattr(requests, method)(url, timeout=10)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
            ) as e:
                if attempt == retries - 1:
                    raise
                print(f"Retry {attempt + 1}/{retries} for {url}: {e}")
                time.sleep(delay)

    def tearDown(self):
        # Kill any lingering processes (cross-platform)
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
        else:
            subprocess.run(["pkill", "-f", "python3 examples/"], capture_output=True)

    def test_05_templates(self):
        print("Testing 05_templates.py...")
        proc = self.run_example("templates/05_templates.py", 5004)
        try:
            r = self.request_with_retry("http://127.0.0.1:5004/")
            self.assertEqual(r.status_code, 200)
            self.assertIn("<h1>Welcome, Rustacean!</h1>", r.text)
            self.assertIn("<li>Fast</li>", r.text)
        except Exception as e:
            print(f"Test 05 failed: {e}")
            self.kill_process(proc)
            out, err = proc.communicate()
            print(f"STDOUT: {out.decode()}")
            print(f"STDERR: {err.decode()}")
            raise e
        finally:
            try:
                if sys.platform == "win32":
                    proc.terminate()
                else:
                    self.kill_process(proc)
            except (ProcessLookupError, OSError):
                pass

    def test_06_blueprints(self):
        print("Testing 06_blueprints.py...")
        proc = self.run_example("routing/06_blueprints.py", 5005)
        try:
            # Check main page
            r = requests.get("http://127.0.0.1:5005/")
            self.assertEqual(r.status_code, 200)
            self.assertIn("Blueprints Example", r.text)

            # Check API blueprint
            r = requests.get("http://127.0.0.1:5005/api/v1/status")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json(), {"status": "ok", "version": 1})

            # Check Admin blueprint
            r = requests.get("http://127.0.0.1:5005/admin/dashboard")
            self.assertEqual(r.status_code, 200)
            self.assertIn("Admin Dashboard", r.text)
        except Exception as e:
            print(f"Test 06 failed: {e}")
            self.kill_process(proc)
            out, err = proc.communicate()
            print(f"STDOUT: {out.decode()}")
            print(f"STDERR: {err.decode()}")
            raise e
        finally:
            try:
                self.kill_process(proc)
            except ProcessLookupError:
                pass

    def test_07_database(self):
        print("Testing 07_database_raw.py...")
        # Use a fresh DB file or cleanup would be nice, but it creates 'example.db' in cwd.
        # We allow it to use the default one for now.
        proc = self.run_example("database/07_database_raw.py", 5006)
        try:
            # Init DB
            r = requests.get("http://127.0.0.1:5006/init-db")
            self.assertEqual(r.status_code, 200)

            # List items
            r = requests.get("http://127.0.0.1:5006/items")
            self.assertEqual(r.status_code, 200)
            data = r.json()
            self.assertTrue(len(data) >= 2)
            self.assertEqual(data[0]["name"], "Rust")
        except Exception as e:
            print(f"Test 07 failed: {e}")
            self.kill_process(proc)
            out, err = proc.communicate()
            print(f"STDOUT: {out.decode()}")
            print(f"STDERR: {err.decode()}")
            raise e
        finally:
            try:
                self.kill_process(proc)
            except ProcessLookupError:
                pass
            if os.path.exists("example.db"):
                os.remove("example.db")

    def test_08_auto_docs(self):
        print("Testing 08_auto_docs.py...")
        proc = self.run_example("advanced/08_auto_docs.py", 5007)
        try:
            # Check Swagger UI
            r = requests.get("http://127.0.0.1:5007/docs")
            self.assertEqual(r.status_code, 200)
            self.assertIn("swagger-ui", r.text)

            # Check OpenAPI JSON
            r = requests.get("http://127.0.0.1:5007/openapi.json")
            self.assertEqual(r.status_code, 200)
            schema = r.json()
            self.assertEqual(schema["info"]["title"], "My Documented API")
            self.assertIn("/items", schema["paths"])
        except Exception as e:
            print(f"Test 08 failed: {e}")
            self.kill_process(proc)
            out, err = proc.communicate()
            print(f"STDOUT: {out.decode()}")
            print(f"STDERR: {err.decode()}")
            raise e
        finally:
            try:
                self.kill_process(proc)
            except ProcessLookupError:
                pass

    def test_09_complex_routing(self):
        print("Testing 09_complex_routing.py...")
        proc = self.run_example("routing/09_complex_routing.py", 5008)
        try:
            r = requests.get("http://127.0.0.1:5008/user/42/profile")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["user_id"], 42)

            r = requests.get("http://127.0.0.1:5008/api/v2/products/99")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["product_id"], 99)
            self.assertEqual(r.json()["api_version"], "v2")
        except Exception as e:
            print(f"Test 09 failed: {e}")
            self.kill_process(proc)
            out, err = proc.communicate()
            print(f"STDOUT: {out.decode()}")
            print(f"STDERR: {err.decode()}")
            raise e
        finally:
            try:
                self.kill_process(proc)
            except ProcessLookupError:
                pass

    def test_10_sqlmodel(self):
        print("Testing 10_database_sqlmodel.py...")
        # Note: 10_database_sqlmodel uses 'example_sqlmodel.db'
        proc = self.run_example("database/10_database_sqlmodel.py", 5010)
        try:
            # Init DB
            r = self.request_with_retry("http://127.0.0.1:5010/init-db")
            self.assertEqual(r.status_code, 200)

            # List items
            r = self.request_with_retry("http://127.0.0.1:5010/items")
            self.assertEqual(r.status_code, 200)
            data = r.json()
            self.assertTrue(len(data) >= 2)
            self.assertEqual(data[0]["name"], "Rust")

            # Get Item
            item_id = data[0]["id"]
            r = self.request_with_retry(f"http://127.0.0.1:5010/items/{item_id}")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["name"], "Rust")

        except Exception as e:
            print(f"Test 10 failed: {e}")
            self.kill_process(proc)
            out, err = proc.communicate()
            print(f"STDOUT: {out.decode()}")
            print(f"STDERR: {err.decode()}")
            raise e
        finally:
            try:
                self.kill_process(proc)
            except ProcessLookupError:
                pass
            if os.path.exists("example_sqlmodel.db"):
                os.remove("example_sqlmodel.db")


if __name__ == "__main__":
    unittest.main()
