"""
FRES Admin Handler
/api/admin/stats
/api/admin/users
/api/admin/users/<id>/status
/api/admin/suggestions
/api/admin/suggestions/<id>/reply
/api/admin/announcements
"""
from flask import request, jsonify
from db import get_db

def stats_handler(req):
    db = get_db()
    total_users = db.execute("SELECT COUNT(*) as n FROM users").fetchone()["n"]
    total_sug   = db.execute("SELECT COUNT(*) as n FROM suggestions").fetchone()["n"]
    total_gen   = db.execute("SELECT COUNT(*) as n FROM chat_logs").fetchone()["n"]
    db.close()
    return jsonify({
        "total_users": total_users,
        "total_suggestions": total_sug,
        "total_generations": total_gen,
    }), 200

def get_users_handler(req):
    db = get_db()
    rows = db.execute(
        "SELECT id, username, role, status, registered_at FROM users ORDER BY id DESC"
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

def update_user_status_handler(req, user_id):
    data = req.get_json() or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({"success": False, "error": "Missing 'status' field."}), 400

    db = get_db()
    result = db.execute(
        "UPDATE users SET status = ? WHERE id = ? AND role != 'admin'",
        (new_status, user_id)
    )
    db.commit()
    rowcount = result.rowcount
    db.close()
    if rowcount == 0:
        return jsonify({"success": False, "error": "User not found or protected."}), 404
    return jsonify({"success": True}), 200

def get_suggestions_handler(req):
    db = get_db()
    rows = db.execute(
        "SELECT id, username, text, reply, timestamp FROM suggestions ORDER BY id DESC"
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

def reply_suggestion_handler(req, sug_id):
    data = req.get_json() or {}
    reply = data.get("reply", "").strip()
    if not reply:
        return jsonify({"success": False, "error": "Reply cannot be empty."}), 400

    db = get_db()
    result = db.execute(
        "UPDATE suggestions SET reply = ? WHERE id = ?", (reply, sug_id)
    )
    db.commit()
    rowcount = result.rowcount
    db.close()
    if rowcount == 0:
        return jsonify({"success": False, "error": "Suggestion not found."}), 404
    return jsonify({"success": True}), 200

def get_announcements_handler(req):
    db = get_db()
    rows = db.execute(
        "SELECT message, created_at FROM announcements ORDER BY id DESC"
    ).fetchall()
    db.close()
    return jsonify([r["message"] for r in rows]), 200

def post_announcement_handler(req):
    data = req.get_json() or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"success": False, "error": "Message cannot be empty."}), 400

    db = get_db()
    db.execute("INSERT INTO announcements (message) VALUES (?)", (message,))
    db.commit()
    db.close()
    return jsonify({"success": True}), 201
