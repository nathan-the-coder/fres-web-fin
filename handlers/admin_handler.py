"""
FRES Admin Handler
/api/admin/stats
/api/admin/users
/api/admin/users/<id>/status
/api/admin/suggestions
/api/admin/suggestions/<id>/reply
/api/admin/announcements
"""
import sqlite3
from db import get_db
import json

def stats_handler(req):
    db = get_db()
    total_users = db.execute("SELECT COUNT(*) as n FROM users").fetchone()["n"]
    total_sug   = db.execute("SELECT COUNT(*) as n FROM suggestions").fetchone()["n"]
    total_gen   = db.execute("SELECT COUNT(*) as n FROM chat_logs").fetchone()["n"]
    db.close()
    return {"total_users": total_users, "total_suggestions": total_sug, "total_generations": total_gen}

def get_users_handler(req):
    db = get_db()
    rows = db.execute("SELECT id, username, role, status, registered_at FROM users ORDER BY id DESC").fetchall()
    db.close()
    return [dict(r) for r in rows]

def update_user_status_handler(req, user_id):
    data = req.get('body', {}) if isinstance(req, dict) else {}
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            data = {}
    new_status = data.get("status")
    if not new_status:
        return {"success": False, "error": "Missing 'status' field."}, 400
    
    db = get_db()
    result = db.execute(
        "UPDATE users SET status = ? WHERE id = ? AND role != 'admin'",
        (new_status, user_id)
    )
    db.commit()
    rowcount = result.rowcount
    db.close()
    if rowcount == 0:
        return {"success": False, "error": "User not found or protected."}, 404
    return {"success": True}, 200

def get_suggestions_handler(req):
    db = get_db()
    rows = db.execute("SELECT id, username, text, reply, timestamp FROM suggestions ORDER BY id DESC").fetchall()
    db.close()
    return [dict(r) for r in rows]

def reply_suggestion_handler(req, sug_id):
    data = req.get('body', {}) if isinstance(req, dict) else {}
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            data = {}
    reply = data.get("reply", "").strip()
    if not reply:
        return {"success": False, "error": "Reply cannot be empty."}, 400
    
    db = get_db()
    result = db.execute("UPDATE suggestions SET reply = ? WHERE id = ?", (reply, sug_id))
    db.commit()
    rowcount = result.rowcount
    db.close()
    if rowcount == 0:
        return {"success": False, "error": "Suggestion not found."}, 404
    return {"success": True}, 200

def get_announcements_handler(req):
    db = get_db()
    rows = db.execute("SELECT message, created_at FROM announcements ORDER BY id DESC").fetchall()
    db.close()
    return [r["message"] for r in rows]

def post_announcement_handler(req):
    data = req.get('body', {}) if isinstance(req, dict) else {}
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            data = {}
    message = (data.get("message") or "").strip()
    if not message:
        return {"success": False, "error": "Message cannot be empty."}, 400
    
    db = get_db()
    db.execute("INSERT INTO announcements (message) VALUES (?)", (message,))
    db.commit()
    db.close()
    return {"success": True}, 201

def submit_suggestion_handler(req):
    data = req.get('body', {}) if isinstance(req, dict) else {}
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            data = {}
    username = data.get('username', 'Anonymous').strip()
    text = data.get('text', '').strip()
    if not text:
        return {"success": False, "error": "Suggestion text cannot be empty."}, 400
    db = get_db()
    db.execute("INSERT INTO suggestions (username, text) VALUES (?, ?)", (username, text))
    db.commit()
    db.close()
    return {"success": True}, 201
