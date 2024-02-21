
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import parse_qs

from youtube_html_parser.parser import parse_yt_page


HERE = Path(__file__).parent
PROJECT_ROOT = HERE.parent.parent

CLI_EXE = PROJECT_ROOT / "cli.exe"

assert CLI_EXE.exists()


def invoke_parse_py(html: str) -> str:
    parsed_data = parse_yt_page(html)
    return parsed_data.serialize()


def invoke_parse_cli(html: str) -> str:
    args = [str(CLI_EXE)]
    with tempfile.TemporaryDirectory() as temp_dir:
        cwd = Path(temp_dir)
        inputfile = cwd / "temp.html"
        outfile = cwd / "temp.json"
        inputfile.write_text(html, encoding="utf-8")
        args.extend(["--input-html", "temp.html"])
        args.extend(["--output-json", "temp.json"])
        result = subprocess.run(args, shell=True, cwd=cwd, check=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to run {CLI_EXE} with args: {args}")
        # read the output file
        out = outfile.read_text(encoding="utf-8")
        return out

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):  # pylint: disable=invalid-name
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        post_data = parse_qs(body.decode("utf-8"))

        html_content = post_data.get("html", [None])[0]
        response = BytesIO()
        if html_content:
            try:
                # Parse the YouTube page HTML content
                json_str = invoke_parse_cli(html_content)
                # parsed_json = parsed_data.to_json()  # Make sure your parse_yt_page returns an object with a to_json() method or adjust accordingly
                response.write(json_str.encode("utf-8"))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(response.getvalue())
            except Exception as e:  # pylint: disable=broad-except
                self.send_response(500)
                self.end_headers()
                response.write(f"Error processing the HTML: {str(e)}".encode("utf-8"))
                self.wfile.write(response.getvalue())
        else:
            self.send_response(400)
            self.end_headers()
            response.write(b'Bad Request: Missing "html" field in POST data')
            self.wfile.write(response.getvalue())


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ("127.0.0.1", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
