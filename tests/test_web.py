import unittest
import subprocess
import time
import requests
import sys
from pathlib import Path

PYTHON_EXE = sys.executable

HERE = Path(__file__).parent
DATA_DIR = HERE / "data"
assert DATA_DIR.exists()

TEST_HTML = list(DATA_DIR.glob("*.html"))
# Filter out *.pretty.html files
TEST_HTML = [file for file in TEST_HTML if not file.name.endswith(".pretty.html")]

class TestSimpleHTTPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the HTTP server as a separate process
        cls.server_process = subprocess.Popen([PYTHON_EXE, '-m', 'youtube_html_parser.web'])
        time.sleep(1)  # Wait a bit for the server to start
        if cls.server_process.poll() is not None:
            raise RuntimeError('Failed to start the HTTP server')

    @classmethod
    def tearDownClass(cls):
        # Terminate the HTTP server process
        cls.server_process.terminate()
        cls.server_process.wait()

    def test_post_html_content(self):
        # The HTML content to test
        html_content = TEST_HTML[0].read_text(encoding="utf-8")
        # Send a POST request to the server with the HTML content
        start = time.time()
        response = requests.post('http://127.0.0.1:8000', data={'html': html_content})
        diff = time.time() - start
        print(f"Time: {diff}")
        # Check that the response is OK
        self.assertEqual(response.status_code, 200, f"Response: {response.content.decode('utf-8')}")
        # Add more assertions here to validate the response content

    @unittest.skip("Not implemented yet.")
    def test_post_without_html_content(self):
        # Send a POST request without HTML content
        response = requests.post('http://127.0.0.1:8000')
        # Check that the response indicates a bad request
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
