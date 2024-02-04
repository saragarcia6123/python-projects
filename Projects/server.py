from http.server import HTTPServer
from http.server import HTTPServer, BaseHTTPRequestHandler

class HelloHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = bytes("Hello", "utf-8")
        self.protocol_version = "HTTP/1.1"
        self.send_response(200)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

server_address = ('localhost', 80)
httpd = HTTPServer(server_address, HelloHandler)
try:
    print('Server started on port 80...')
    httpd.serve_forever()
except KeyboardInterrupt:
    print('Stopping server...')
    httpd.server_close()