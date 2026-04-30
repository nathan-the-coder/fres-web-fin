import json
import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Auto-load .env
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ[_k.strip()] = _v.strip()

from db import init_db, get_db
from handlers import users_handler, admin_handler, ai_handler

def handler(request, response):
    path = request.get("path", "/").split('?')[0]
    method = request.get("method", "GET")
    
    # Parse body
    body = request.get("body", "{}")
    try:
        data = json.loads(body) if body else {}
    except:
        data = {}
    
    # Route
    if path == "/api/ping" and method == "GET":
        return {"status": "online", "message": "FRES Backend active!", "version": "2.0.0"}
    elif path == "/api/users/login" and method == "POST":
        return users_handler.login_handler(data)
    elif path == "/api/users/register" and method == "POST":
        return users_handler.register_handler(data)
    elif path == "/api/admin/stats" and method == "GET":
        return admin_handler.stats_handler()
    else:
        return {"error": "Not found"}, 404

if __name__ == "__main__":
    print("Vercel serverless function")
