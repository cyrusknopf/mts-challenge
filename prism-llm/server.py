import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable

from llm import MODEL, get_response, init_model


class PRISMServer(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        # Set default response values
        self.response_data = ""
        content_type = "text/plain"
        self.status_code = 403
        self.response_data = "GET not allowed"

        # Send response
        self.send_response(self.status_code)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(self.response_data.encode("utf-8"))

    def do_POST(self):
        """Handle POST requests with data processing"""
        try:
            if self.path != "/generate":
                response = {
                    "status": 400,
                    "body": f"Wrong endpoint: {self.path}\n Please POST request to /generate",
                }
                # Send response
                self.send_response(response["status"])
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response["body"]).encode())

            # Get content length and headers
            content_length = int(self.headers.get("Content-Length", 0))
            content_type = self.headers.get("Content-Type", "")

            # Read POST data
            post_data = self.rfile.read(content_length)

            # Process different content types
            if content_type == "application/json":
                data = json.loads(post_data)
                llm_response = get_response(self.model, self.tokenizer, data)
                response = {"status": 200, "body": f"{(llm_response)}"}
            else:
                response = {"status": 400, "body": "Unsupported content type"}
        except Exception as e:
            response = {"status": 500, "body": f"Error processing request: {str(e)}"}

        # Send response
        self.send_response(response["status"])
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response["body"]).encode())


class PRISMHTTPServer(HTTPServer):
    def __init__(
        self,
        server_address: Any,
        RequestHandlerClass: Callable,
        tokenizer: Any,
        model: Any,
        bind_and_activate: bool = True,
    ) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.RequestHandlerClass.model = model
        self.RequestHandlerClass.tokenizer = tokenizer


def run_server(port):
    tokenizer, model = init_model(MODEL)

    server_address = ("", port)

    httpd = PRISMHTTPServer(server_address, PRISMServer, tokenizer, model)
    print(f"Server running on port {port}")

    httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("prism-llm-server")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        required=True,
        help="Specify the port that the server will run on.",
    )
    args = parser.parse_args()
    run_server(args.port)
