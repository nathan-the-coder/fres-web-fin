"""
FRES Admin Handler
/api/admin/stats
/api/admin/users
/api/admin/users/<id>/status
/api/admin/suggestions
/api/admin/suggestions/<id>/reply
/api/admin/announcements
"""


def stats(handler, match):
    total_users = handler.db.execute("SELECT COUNT(*) as n FROM users").fetchone()["n"]
    total_sug   = handler.db.execute("SELECT COUNT(*) as n FROM suggestions").fetchone()["n"]
    total_gen   = handler.db.execute("SELECT COUNT(*) as n FROM chat_logs").fetchone()["n"]
    return handler._send_json({
        "total_users": total_users,
        "total_suggestions": total_sug,
        "total_generations": total_gen,
    })


def get_users(handler, match):
    rows = handler.db.execute(
        "SELECT id, username, role, status, registered_at FROM users ORDER BY id DESC"
    ).fetchall()
    return handler._send_json([dict(r) for r in rows])


def update_user_status(handler, match):
    user_id = int(match.group(1))
    new_status = handler.body.get("status")
    if not new_status:
        return handler._send_json({"success": False, "error": "Missing 'status' field."}, 400)

    result = handler.db.execute(
        "UPDATE users SET status = ? WHERE id = ? AND role != 'admin'",
        (new_status, user_id)
    )
    handler.db.commit()
    if result.rowcount == 0:
        return handler._send_json({"success": False, "error": "User not found or protected."}, 404)
    return handler._send_json({"success": True})


def get_suggestions(handler, match):
    rows = handler.db.execute(
        "SELECT id, username, text, reply, timestamp FROM suggestions ORDER BY id DESC"
    ).fetchall()
    return handler._send_json([dict(r) for r in rows])


def reply_suggestion(handler, match):
    sug_id = int(match.group(1))
    reply = handler.body.get("reply", "").strip()
    if not reply:
        return handler._send_json({"success": False, "error": "Reply cannot be empty."}, 400)

    result = handler.db.execute(
        "UPDATE suggestions SET reply = ? WHERE id = ?", (reply, sug_id)
    )
    handler.db.commit()
    if result.rowcount == 0:
        return handler._send_json({"success": False, "error": "Suggestion not found."}, 404)
    return handler._send_json({"success": True})


def get_announcements(handler, match):
    rows = handler.db.execute(
        "SELECT message, created_at FROM announcements ORDER BY id DESC"
    ).fetchall()
    # Return list of strings for backward-compat with frontend
    return handler._send_json([r["message"] for r in rows])


def post_announcement(handler, match):
    message = (handler.body.get("message") or "").strip()
    if not message:
        return handler._send_json({"success": False, "error": "Message cannot be empty."}, 400)

    handler.db.execute("INSERT INTO announcements (message) VALUES (?)", (message,))
    handler.db.commit()
    return handler._send_json({"success": True})
