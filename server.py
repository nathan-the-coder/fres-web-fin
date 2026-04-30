import json
import os
import re
import sqlite3
import urllib.parse
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# ─── Auto-load .env (no python-dotenv needed) ────────────────────────────────
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ[_k.strip()] = _v.strip()

from db import init_db, get_db
from handlers import users_handler, admin_handler, ai_handler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FRES")

# ─── Router Table ────────────────────────────────────────────────────────────
ROUTES = {
    ("GET",  r"^/api/ping$"):                              lambda h, m: h._send_json({"status": "online", "message": "FRES Backend active!", "version": "2.0.0"}),
    ("POST", r"^/api/users/login$"):                       users_handler.login,
    ("POST", r"^/api/users/register$"):                    users_handler.register,
    ("GET",  r"^/api/admin/stats$"):                       admin_handler.stats,
    ("GET",  r"^/api/admin/users$"):                       admin_handler.get_users,
    ("PUT",  r"^/api/admin/users/(\d+)/status$"):          admin_handler.update_user_status,
    ("GET",  r"^/api/admin/suggestions$"):                 admin_handler.get_suggestions,
    ("POST", r"^/api/admin/suggestions/(\d+)/reply$"):     admin_handler.reply_suggestion,
    ("GET",  r"^/api/admin/announcements$"):               admin_handler.get_announcements,
    ("POST", r"^/api/admin/announcements$"):               admin_handler.post_announcement,
    ("POST", r"^/api/ai/generate$"):                       ai_handler.generate,
    ("GET",  r"^/api/ai/logs$"):                           ai_handler.get_logs,
}

class FRESHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        logger.info(f"{self.address_string()} - {fmt % args}")

    # ── CORS Headers ────────────────────────────────────────────────────────
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    # ── Response helpers ────────────────────────────────────────────────────
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    # ── Router ───────────────────────────────────────────────────────────────
    def _dispatch(self, method):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        for (route_method, pattern), handler in ROUTES.items():
            if route_method != method:
                continue
            m = re.match(pattern, path)
            if m:
                self.body = self._read_body() if method in ("POST", "PUT") else {}
                self.url_params = m.groups()
                self.db = get_db()
                try:
                    handler(self, m)
                except Exception as e:
                    logger.error(f"Handler error: {e}", exc_info=True)
                    self._send_json({"success": False, "error": "Internal server error"}, 500)
                finally:
                    self.db.close()
                return

        # Serve static files
        if method == "GET":
            self._serve_static(path)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_GET(self):  self._dispatch("GET")
    def do_POST(self): self._dispatch("POST")
    def do_PUT(self):  self._dispatch("PUT")

    # ── Static File Server ───────────────────────────────────────────────────
    def _serve_static(self, path):
        MIME = {
            ".html": "text/html", ".css": "text/css", ".js": "application/javascript",
            ".png": "image/png",  ".jpg": "image/jpeg", ".svg": "image/svg+xml",
            ".ico": "image/x-icon", ".txt": "text/plain"
        }

        if path == "/" or path == "":
            path = "/index.html"

        # Try root directory first
        relative_path = path.lstrip("/")
        filepath = Path(__file__).parent / relative_path
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
    if os.environ.get("OPENROUTER_API_KEY"):
        logger.info("OPENROUTER_API_KEY loaded from environment.")
    else:
        logger.warning("OPENROUTER_API_KEY is not set. AI generation will fail. Get one at https://openrouter.ai")

    PORT = int(os.environ.get("PORT", 5000))
    HOST = "0.0.0.0"
    init_db()
    logger.info(f"🚀 FRES Backend running at http://{HOST}:{PORT}")
    server = HTTPServer((HOST, PORT), FRESHandler)
    server.serve_forever()
