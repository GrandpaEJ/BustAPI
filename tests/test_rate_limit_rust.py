import time
import unittest

from bustapi import BustAPI, RateLimit
from bustapi.core.exceptions import TooManyRequests


class TestRateLimit(unittest.TestCase):
    def setUp(self):
        self.app = BustAPI()
        self.limiter = RateLimit(self.app)

    def test_limit_decorator(self):
        # Define a limited route
        @self.limiter.limit("2/second")
        def limited_view():
            return "ok"

        # Context required for request.remote_addr access
        with self.app.test_request_context():
            # First call: Allowed
            self.assertEqual(limited_view(), "ok")

            # Second call: Allowed
            self.assertEqual(limited_view(), "ok")

            # Third call: Blocked
            with self.assertRaises(TooManyRequests):
                limited_view()

        # Wait a bit (simulated)
        # Note: Rust uses system time, so we'd have to actually sleep to test expiry integration-style,
        # but unit test is fine just verifying the kick-in.

    def test_parse_limit_string(self):
        c, p = self.limiter._parse_limit_string("10/minute")
        self.assertEqual(c, 10)
        self.assertEqual(p, 60)

        c, p = self.limiter._parse_limit_string("5/s")
        self.assertEqual(c, 5)
        self.assertEqual(p, 1)


if __name__ == "__main__":
    unittest.main()
