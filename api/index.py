from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from pathlib import Path

# Setup
sys.path.insert(0, str(Path(__file__).parent.parent))

# Auto-load .env
_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ[_k.strip()] = _v.strip()

from db import init_db, get_db
from handlers import users_handler, admin_handler, ai_handler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._dispatch("GET")
    
    def do_POST(self):
        self._dispatch("POST")
    
    def _dispatch(self, method):
        path = self.path.split('?')[0]
        
        if path == "/api/ping" and method == "GET":
            self._send_json({"status": "online", "message": "FRES Backend active!", "version": "2.0.0"})
        elif path == "/api/users/login" and method == "POST":
            users_handler.login(self, None)
        elif path == "/api/users/register" and method == "POST":
            users_handler.register(self, None)
        else:
            self._serve_static(path)
    
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def _serve_static(self, path):
        MIME = {
            ".html": "text/html", ".css": "text/css", ".js": "application/javascript",
            ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml",
            ".ico": "image/x-icon", ".txt": "text/plain"
        }
        
        if path == "/" or path == "":
            path = "/index.html"
        
        filepath = Path(__file__).parent.parent / path.lstrip("/")
        if filepath.is_file():
            ext = filepath.suffix.lower()
            mime = MIME.get(ext, "application/octet-stream")
            data = filepath.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
            return
        
        self._send_json({"error": "Not Found"}, 404)

if __name__ == "__main__":
    print("Vercel serverless function")
