"""
FRES Users Handler
/api/users/login
/api/users/register
"""
import hashlib
import json
from db import get_db

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def login_handler(req):
    # Parse request body
    if hasattr(req, 'get_json'):
        # Flask request
        data = req.get_json() or {}
    else:
        # Vercel serverless function request
        body = req.get('body', '{}')
        try:
            data = json.loads(body)
        except:
            data = {}
    
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    
    if not username or not password:
        return {"success": False, "error": "Username and password required."}, 400
    
    db = get_db()
    row = db.execute(
        "SELECT id, username, role, status, password FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    db.close()
    
    if not row or row["password"] != hash_pw(password):
        return {"success": False, "error": "Invalid username or password."}, 401
    
    if row["status"] == "Deleted":
        return {"success": False, "error": "This account has been deactivated."}, 403
    
    return {
        "success": True,
        "id":       row["id"],
        "username": row["username"],
        "role":     row["role"],
        "status":   row["status"],
    }, 200

def register_handler(req):
    # Parse request body
    if hasattr(req, 'get_json'):
        data = req.get_json() or {}
    else:
        body = req.get('body', '{}')
        try:
            data = json.loads(body)
        except:
            data = {}
    
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    
    if not username or not password:
        return {"success": False, "error": "Username and password required."}, 400
    
    if len(username) < 3:
        return {"success": False, "error": "Username must be at least 3 characters."}, 400
    
    if len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters."}, 400
    
    db = get_db()
    existing = db.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    
    if existing:
        db.close()
        return {"success": False, "error": "Username already taken."}, 409
    
    db.execute(
        "INSERT INTO users (username, password, role, status) VALUES (?, ?, 'user', 'active')",
        (username, hash_pw(password)))
    db.commit()
    db.close()
    return {"success": True, "message": "Registered successfully!"}, 201
