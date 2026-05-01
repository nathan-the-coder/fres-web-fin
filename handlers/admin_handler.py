"""
FRES Admin Handler
/api/admin/stats
/api/admin/users
/api/admin/users/<id>/status
/api/admin/suggestions
/api/admin/suggestions/<id>/reply
/api/admin/announcements
"""
import json
from db import get_db

def _parse_request(req):
    """Parse request data from Flask request or plain dict."""
    data = {}
    try:
        if hasattr(req, 'get_json'):
            data = req.get_json(force=True)
        elif isinstance(req, dict):
            data = req.get('body', req)
            if isinstance(data, str):
                data = json.loads(data)
        if not isinstance(data, dict):
            data = {}
    except Exception as e:
        print(f"Parse error: {e}")
        data = {}
    return data

def stats_handler(req):
    db = get_db()
    total_users = db.execute("SELECT COUNT(*) as n FROM users").fetchone()["n"]
    total_sug = db.execute("SELECT COUNT(*) as n FROM suggestions").fetchone()["n"]
    total_gen = db.execute("SELECT COUNT(*) as n FROM chat_logs").fetchone()["n"]
    db.close()
    return {"total_users": total_users, "total_suggestions": total_sug, "total_generations": total_gen}

def get_users_handler(req):
    db = get_db()
    rows = db.execute("SELECT id, username, role, status, registered_at FROM users ORDER BY id DESC").fetchall()
    db.close()
    return [dict(r) for r in rows]

def update_user_status_handler(req, user_id):
    data = _parse_request(req)
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
    data = _parse_request(req)
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
    data = _parse_request(req)
    message = (data.get("message") or "").strip()
    if not message:
        return {"success": False, "error": "Message cannot be empty."}, 400

    db = get_db()
    db.execute("INSERT INTO announcements (message) VALUES (?)", (message,))
    db.commit()
    db.close()
    return {"success": True}, 201

def submit_suggestion_handler(req):
    data = _parse_request(req)
    username = data.get('username', 'Anonymous').strip()
    text = data.get('text', '').strip()
    if not text:
        return {"success": False, "error": "Suggestion text cannot be empty."}, 400
    db = get_db()
    db.execute("INSERT INTO suggestions (username, text) VALUES (?, ?)", (username, text))
    db.commit()
    db.close()
    return {"success": True}, 201
