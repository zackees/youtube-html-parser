import concurrent.futures
import subprocess
import sys
import time
import unittest
from pathlib import Path

import requests

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
        cls.server_process = subprocess.Popen(  # pylint: disable=consider-using-with
            [PYTHON_EXE, "-m", "youtube_html_parser.web"]
        )
        time.sleep(1)  # Wait a bit for the server to start
        if cls.server_process.poll() is not None:
            raise RuntimeError("Failed to start the HTTP server")

    @classmethod
    def tearDownClass(cls):
        # Terminate the HTTP server process
        cls.server_process.terminate()
        cls.server_process.wait()

    def post_html_content(self, html_content):
        """Function to send a POST request with HTML content."""
        response = requests.post(
            "http://127.0.0.1:8000", data={"html": html_content}, timeout=60
        )
        return response

    def test_post_html_content(self):
        # The HTML content to test
        html_contents = [
            html_file.read_text(encoding="utf-8") for html_file in TEST_HTML
        ]  # Assuming you want to use up to 16 HTML files
        html = html_contents[0]

        # Record the start time
        start = time.time()

        num_requests = 8

        # Use ThreadPoolExecutor to post HTML content concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all POST requests and get Future objects
            future_to_html = {
                executor.submit(self.post_html_content, html): html
                for i in range(num_requests)
            }

            # Wait for the futures to complete and validate the responses
            for future in concurrent.futures.as_completed(future_to_html):
                html = future_to_html[future]
                try:
                    response = future.result()
                    # Check that the response is OK
                    self.assertEqual(
                        response.status_code,
                        200,
                        f"Response for {html[:30]}...: {response.content.decode('utf-8')}",
                    )
                except Exception as exc:  # pylint: disable=broad-except
                    self.fail(f"HTML content generated an exception: {exc}")

        # Print the total time taken
        diff = time.time() - start
        print(f"Total time for {num_requests} requests: {diff}")

    @unittest.skip("Not implemented yet.")
    def test_post_without_html_content(self):
        # Send a POST request without HTML content
        response = requests.post("http://127.0.0.1:8000", timeout=60)
        # Check that the response indicates a bad request
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
