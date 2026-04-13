"""
FRES Users Endpoint - Vercel Serverless Function
/api/users/login
/api/users/register
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from base import get_db, hash_pw, parse_body, success_response, error_response, cors_preflight


def login(event):
    """Handle /api/users/login requests."""
    data = parse_body(event)
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return error_response("Username and password required.", 400)

    db = get_db()
    row = db.execute(
        "SELECT id, username, role, status, password FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    db.close()

    if not row or row["password"] != hash_pw(password):
        return error_response("Invalid username or password.", 401)

    if row["status"] == "Deleted":
        return error_response("This account has been deactivated.", 403)

    return success_response({
        "id": row["id"],
        "username": row["username"],
        "role": row["role"],
        "status": row["status"],
    })


def register(event):
    """Handle /api/users/register requests."""
    data = parse_body(event)
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return error_response("Username and password required.", 400)

    if len(username) < 3:
        return error_response("Username must be at least 3 characters.", 400)

    if len(password) < 6:
        return error_response("Password must be at least 6 characters.", 400)

    db = get_db()
    existing = db.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()

    if existing:
        db.close()
        return error_response("Username already taken.", 409)

    db.execute(
        "INSERT INTO users (username, password, role, status) VALUES (?, ?, 'user', 'active')",
        (username, hash_pw(password))
    )
    db.commit()
    db.close()

    return success_response({"message": "Registered successfully!"}, 201)


def main(event, context):
    """Main entry point for Vercel serverless function."""
    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return cors_preflight(event)

    # Route to appropriate handler
    path = event.get("path", "")

    if "login" in path:
        return login(event)
    elif "register" in path:
        return register(event)
    else:
        return error_response("Unknown user endpoint", 404)
