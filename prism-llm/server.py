from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from llm import init_model, MODEL

class PRISMServer(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        # Set default response values
        self.response_data = ""
        self.status_code = 200
        content_type = "text/plain"

        # Route handling
        if self.path == "/generate":
            headers = self.headers
            self.response_data = "Generating context"
        else:
            self.status_code = 404
            self.response_data = "Page not found"

        # Send response
        self.send_response(self.status_code)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(self.response_data.encode("utf-8"))

    def do_POST(self):
        """Handle POST requests with data processing"""
        try:
            if (self.path != '/generate'):
                response = {
                    'status': 400,
                    'body': f"Wrong endpoint: {self.path}\n Please POST request to /generate"
                }
                # Send response
                self.send_response(response['status'])
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response['body']).encode())

            # Get content length and headers
            content_length = int(self.headers.get('Content-Length', 0))
            content_type = self.headers.get('Content-Type', '')
            
            # Read POST data
            post_data = self.rfile.read(content_length)
            
            # Process different content types
            if content_type == 'application/json':
                data = json.loads(post_data)
                response = {
                    'status': 200,
                    'body': 'blaaa'
                }
            else:
                response = {
                    'status': 400,
                    'body': 'Unsupported content type'
                }
        except Exception as e:
            response = {
                'status': 500,
                'body': f'Error processing request: {str(e)}'
            }

        # Send response
        self.send_response(response['status'])
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response['body']).encode())



def run_server(port=8001):
    tokenizer, model = init_model(MODEL)

    server_address = ("", port)

    httpd = HTTPServer(server_address, PRISMServer)
    print(f"Server running on port {port}")

    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
