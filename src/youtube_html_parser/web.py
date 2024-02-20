from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from urllib.parse import parse_qs

from youtube_html_parser.parser import parse_yt_page


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
                parsed_data = parse_yt_page(html_content)
                # Convert parsed data to JSON
                json_str = parsed_data.serialize()
                # parsed_json = parsed_data.to_json()  # Make sure your parse_yt_page returns an object with a to_json() method or adjust accordingly
                response.write(json_str)
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
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
