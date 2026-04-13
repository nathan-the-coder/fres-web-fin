"""
FRES Admin Endpoint - Vercel Serverless Function
"""
import os
import sys
import re

sys.path.insert(0, os.path.dirname(__file__))

from base import get_db, parse_body, success_response, error_response, cors_preflight

def handler(event, context):
    """Main entry point for Vercel serverless function."""
    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return cors_preflight(event)

    # Route to appropriate handler based on path and method
    path = event.get("path", "")
    method = event.get("httpMethod", "GET")

    # Stats endpoint
    if "stats" in path and method == "GET":
        return stats(event)

    # Users endpoints
    if path.rstrip("/").endswith("/users") and method == "GET":
        return get_users(event)
    if re.search(r"/api/admin/users/\d+/status", path) and method == "PUT":
        return update_user_status(event)

    # Suggestions endpoints
    if "suggestions" in path and method == "GET":
        return get_suggestions(event)
    if re.search(r"/api/admin/suggestions/\d+/reply", path) and method == "POST":
        return reply_suggestion(event)

    # Announcements endpoints
    if "announcements" in path and method == "GET":
        return get_announcements(event)
    if "announcements" in path and method == "POST":
        return post_announcement(event)

    return error_response("Unknown admin endpoint", 404)


def stats(event):
    """Get admin dashboard statistics."""
    db = get_db()
    total_users = db.execute("SELECT COUNT(*) as n FROM users").fetchone()["n"]
    total_sug = db.execute("SELECT COUNT(*) as n FROM suggestions").fetchone()["n"]
    total_gen = db.execute("SELECT COUNT(*) as n FROM chat_logs").fetchone()["n"]
    db.close()

    return success_response({
        "total_users": total_users,
        "total_suggestions": total_sug,
        "total_generations": total_gen,
    })


def get_users(event):
    """Get all users."""
    db = get_db()
    rows = db.execute(
        "SELECT id, username, role, status, registered_at FROM users ORDER BY id DESC"
    ).fetchall()
    db.close()
    return success_response({"users": [dict(r) for r in rows]})


def update_user_status(event):
    """Update user status (activate/deactivate)."""
    # Extract user_id from path
    path = event.get("path", "")
    match = re.search(r"/api/admin/users/(\d+)/status", path)
    if not match:
        return error_response("Invalid user ID", 400)

    user_id = int(match.group(1))
    data = parse_body(event)
    new_status = data.get("status")

    if not new_status:
        return error_response("Missing 'status' field.", 400)

    db = get_db()
    result = db.execute(
        "UPDATE users SET status = ? WHERE id = ? AND role != 'admin'",
        (new_status, user_id)
    )
    db.commit()
    db.close()

    if result.rowcount == 0:
        return error_response("User not found or protected.", 404)

    return success_response({})


def get_suggestions(event):
    """Get all suggestions."""
    db = get_db()
    rows = db.execute(
        "SELECT id, username, text, reply, timestamp FROM suggestions ORDER BY id DESC"
    ).fetchall()
    db.close()
    return success_response({"suggestions": [dict(r) for r in rows]})


def reply_suggestion(event):
    """Reply to a suggestion."""
    path = event.get("path", "")
    match = re.search(r"/api/admin/suggestions/(\d+)/reply", path)
    if not match:
        return error_response("Invalid suggestion ID", 400)

    sug_id = int(match.group(1))
    data = parse_body(event)
    reply = data.get("reply", "").strip()

    if not reply:
        return error_response("Reply cannot be empty.", 400)

    db = get_db()
    result = db.execute(
        "UPDATE suggestions SET reply = ? WHERE id = ?",
        (reply, sug_id)
    )
    db.commit()
    db.close()

    if result.rowcount == 0:
        return error_response("Suggestion not found.", 404)

    return success_response({})


def get_announcements(event):
    """Get all announcements."""
    db = get_db()
    rows = db.execute(
        "SELECT message, created_at FROM announcements ORDER BY id DESC"
    ).fetchall()
    db.close()
    return success_response({"announcements": [r["message"] for r in rows]})


def post_announcement(event):
    """Create a new announcement."""
    data = parse_body(event)
    message = (data.get("message") or "").strip()

    if not message:
        return error_response("Message cannot be empty.", 400)

    db = get_db()
    db.execute("INSERT INTO announcements (message) VALUES (?)", (message,))
    db.commit()
    db.close()

    return success_response({})
