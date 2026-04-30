from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, re, sqlite3, urllib.parse
from pathlib import Path

# Auto-load .env
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ[k.strip()] = v.strip()

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
        if path in ("", "/"):
            path = "/index.html"
        filepath = Path(__file__).parent / path.lstrip("/")
        if filepath.is_file():
            ext = filepath.suffix.lower()
            mime = {".html": "text/html", ".css": "text/css", ".js": "application/javascript",
                    ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml",
                    ".ico": "image/x-icon", ".txt": "text/plain"}.get(ext, "application/octet-stream")
            data = filepath.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
            return
        self._send_json({"error": "Not Found"}, 404)

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), handler)
    print(f"Running on port {port}")
    server.serve_forever()
