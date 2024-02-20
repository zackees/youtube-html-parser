import unittest
import subprocess
import time
import requests
import sys

PYTHON_EXE = sys.executable

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
        html_content = '<html><body><h1>Hello, World!</h1></body></html>'
        # Send a POST request to the server with the HTML content
        response = requests.post('http://localhost:8000', data={'html': html_content})
        # Check that the response is OK
        self.assertEqual(response.status_code, 200)
        # Add more assertions here to validate the response content

    def test_post_without_html_content(self):
        # Send a POST request without HTML content
        response = requests.post('http://localhost:8000')
        # Check that the response indicates a bad request
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
