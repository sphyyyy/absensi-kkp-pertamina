import unittest
import requests

class TestHTTPServer(unittest.TestCase):
    def test_local_server_if_running(self):
        try:
            r = requests.get('http://127.0.0.1:5000', allow_redirects=True, timeout=2)
            self.assertIn(r.status_code, [200, 302])
        except requests.exceptions.RequestException:
            self.skipTest("Local dev server is not running on port 5000")

if __name__ == '__main__':
    unittest.main()
