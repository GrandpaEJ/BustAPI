
import subprocess
import time
import requests
import unittest
import os
import signal
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PYTHON_PATH = os.path.join(PROJECT_ROOT, "python")

env = os.environ.copy()
env["PYTHONPATH"] = PYTHON_PATH

class TestNewExamples(unittest.TestCase):
    def run_example(self, script, port):
        cmd = [sys.executable, f"examples/{script}"]
        proc = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            preexec_fn=os.setsid,
        )
        time.sleep(2)  # Wait for startup
        return proc

    def tearDown(self):
        # Kill any lingering processes
        subprocess.run(["pkill", "-f", "python3 examples/"], capture_output=True)

    def test_05_templates(self):
        print("Testing 05_templates.py...")
        proc = self.run_example("05_templates.py", 5004)
        try:
            r = requests.get("http://127.0.0.1:5004/")
            self.assertEqual(r.status_code, 200)
            self.assertIn("<h1>Welcome, Rustacean!</h1>", r.text)
            self.assertIn("<li>Fast</li>", r.text)
        finally:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

    def test_06_blueprints(self):
        print("Testing 06_blueprints.py...")
        proc = self.run_example("06_blueprints.py", 5005)
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
        finally:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

    def test_07_database(self):
        print("Testing 07_database_raw.py...")
        # Use a fresh DB file or cleanup would be nice, but it creates 'example.db' in cwd.
        # We allow it to use the default one for now.
        proc = self.run_example("07_database_raw.py", 5006)
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
        finally:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            if os.path.exists("example.db"):
                os.remove("example.db")

    def test_08_auto_docs(self):
        print("Testing 08_auto_docs.py...")
        proc = self.run_example("08_auto_docs.py", 5007)
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
        finally:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

    def test_09_complex_routing(self):
        print("Testing 09_complex_routing.py...")
        proc = self.run_example("09_complex_routing.py", 5008)
        try:
            r = requests.get("http://127.0.0.1:5008/user/42/profile")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["user_id"], 42)

            r = requests.get("http://127.0.0.1:5008/api/v2/products/99")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["product_id"], 99)
            self.assertEqual(r.json()["api_version"], "v2")
        finally:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

if __name__ == "__main__":
    unittest.main()
