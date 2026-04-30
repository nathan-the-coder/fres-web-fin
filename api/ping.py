from http.server import BaseHTTPRequestHandler
from json import dumps

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(dumps({"status": "online", "message": "FRES Backend active!", "version": "2.0.0"}).encode())
