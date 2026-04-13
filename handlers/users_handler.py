"""
FRES Users Handler
/api/users/login
/api/users/register
"""
from db import hash_pw


def login(handler, match):
    data = handler.body
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return handler._send_json({"success": False, "error": "Username and password required."}, 400)

    row = handler.db.execute(
        "SELECT id, username, role, status, password FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if not row or row["password"] != hash_pw(password):
        return handler._send_json({"success": False, "error": "Invalid username or password."}, 401)

    if row["status"] == "Deleted":
        return handler._send_json({"success": False, "error": "This account has been deactivated."}, 403)

    return handler._send_json({
        "success": True,
        "id":       row["id"],
        "username": row["username"],
        "role":     row["role"],
        "status":   row["status"],
    })


def register(handler, match):
    data = handler.body
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return handler._send_json({"success": False, "error": "Username and password required."}, 400)

    if len(username) < 3:
        return handler._send_json({"success": False, "error": "Username must be at least 3 characters."}, 400)

    if len(password) < 6:
        return handler._send_json({"success": False, "error": "Password must be at least 6 characters."}, 400)

    existing = handler.db.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()

    if existing:
        return handler._send_json({"success": False, "error": "Username already taken."}, 409)

    handler.db.execute(
        "INSERT INTO users (username, password, role, status) VALUES (?, ?, 'user', 'active')",
        (username, hash_pw(password))
    )
    handler.db.commit()
    return handler._send_json({"success": True, "message": "Registered successfully!"}, 201)
