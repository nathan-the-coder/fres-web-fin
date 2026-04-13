"""
FRES API - Single Router for Vercel
Handles all /api/* routes
"""
import os
import sys
import json
import re
import sqlite3
import hashlib
from openai import OpenAI

# ============================================================
# Utilities
# ============================================================

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "instance", "fres.db")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def success_response(data, status=200):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept",
        },
        "body": json.dumps({"success": True, **data})
    }

def error_response(message, status=400):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept",
        },
        "body": json.dumps({"success": False, "error": message})
    }

def parse_body(event):
    try:
        body_str = event.get("body", "{}")
        return json.loads(body_str) if isinstance(body_str, str) else body_str
    except:
        return {}

def cors_preflight():
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept",
        },
        "body": ""
    }

# ============================================================
# AI Functions
# ============================================================

OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/auto")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

def _build_prompt(lesson_text, mode, count):
    mode_label = {
        "multipleChoice": "Multiple Choice (A B C D)",
        "trueFalse": "True or False",
        "identification": "Identification / Fill-in-the-blank",
    }.get(mode, "Multiple Choice (A B C D)")
    
    return f"""You are an academic quiz generator for Filipino university students.
Generate exactly {count} {mode_label} questions based ONLY on the text below.

[LESSON TEXT START]
{lesson_text}
[LESSON TEXT END]

OUTPUT FORMAT — follow this EXACTLY, no deviations:

QUESTIONS:
1. [Question]
A. [Option]
B. [Option]
C. [Option]
D. [Option]

2. [Question]
...

ANSWERS:
1. [Letter or True/False or keyword]
2. [Letter or True/False or keyword]
...

Rules:
- Start immediately with "QUESTIONS:" — no preamble
- Every question on its own numbered line
- Choices on separate lines directly below each question
- After all questions, write "ANSWERS:" then number each answer
- Answers section must have exactly {count} entries matching question numbers
- Do not add explanations or extra text
"""

def _call_ai(prompt):
    try:
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set")
        
        client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "You are an academic quiz generator for Filipino university students."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096,
        )
        
        if response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
            return result.strip() if result else None
        return None
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def _parse_ai_response(raw):
    raw = raw.strip()
    parts = re.split(r"\n\s*ANSWERS\s*:\s*\n", raw, flags=re.IGNORECASE, maxsplit=1)
    if len(parts) == 2:
        q = re.sub(r"^QUESTIONS\s*:\s*\n?", "", parts[0].strip(), flags=re.IGNORECASE)
        return {"questions": q, "answers": parts[1].strip()}
    q = re.sub(r"^QUESTIONS\s*:\s*\n?", "", raw, flags=re.IGNORECASE).strip()
    return {"questions": q, "answers": "(Answers not separated)"}

# ============================================================
# Route Handlers
# ============================================================

def handle_ping():
    return success_response({"status": "online", "message": "FRES Backend active!", "version": "2.0.0"})

def handle_users_login(event):
    data = parse_body(event)
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    
    if not username or not password:
        return error_response("Username and password required.", 400)
    
    db = get_db()
    row = db.execute("SELECT id, username, role, status, password FROM users WHERE username = ?", (username,)).fetchone()
    db.close()
    
    if not row or row["password"] != hash_pw(password):
        return error_response("Invalid username or password.", 401)
    if row["status"] == "Deleted":
        return error_response("Account deactivated.", 403)
    
    return success_response({"id": row["id"], "username": row["username"], "role": row["role"], "status": row["status"]})

def handle_users_register(event):
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
    if db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
        db.close()
        return error_response("Username already taken.", 409)
    
    db.execute("INSERT INTO users (username, password, role, status) VALUES (?, ?, 'user', 'active')", (username, hash_pw(password)))
    db.commit()
    db.close()
    return success_response({"message": "Registered successfully!"}, 201)

def handle_ai_generate(event):
    data = parse_body(event)
    lesson_text = (data.get("lesson_text") or data.get("prompt") or "").strip()
    mode = data.get("type", "multipleChoice")
    count = int(data.get("count", 10))
    user_id = data.get("user_id")
    prompt_override = data.get("prompt_override")
    
    if not lesson_text and not prompt_override:
        return error_response("Missing input text.", 400)
    
    final_prompt = prompt_override if prompt_override else _build_prompt(lesson_text, mode, count)
    raw_result = _call_ai(final_prompt)
    
    if raw_result is None:
        return error_response("AI connection failed. Check API key or rate limits.", 503)
    
    parsed = _parse_ai_response(raw_result)
    
    try:
        db = get_db()
        db.execute("INSERT INTO chat_logs (user_id, prompt, response) VALUES (?, ?, ?)", (user_id, (lesson_text or final_prompt)[:500], raw_result[:2000]))
        db.commit()
        db.close()
    except Exception as e:
        print(f"DB log error: {e}")
    
    return success_response({"questions": parsed["questions"], "answers": parsed["answers"], "raw": raw_result})

def handle_ai_logs(event):
    db = get_db()
    rows = db.execute("SELECT id, user_id, prompt, created_at FROM chat_logs ORDER BY id DESC LIMIT 50").fetchall()
    db.close()
    return success_response({"logs": [dict(r) for r in rows]})

def handle_admin_stats(event):
    db = get_db()
    total_users = db.execute("SELECT COUNT(*) as n FROM users").fetchone()["n"]
    total_sug = db.execute("SELECT COUNT(*) as n FROM suggestions").fetchone()["n"]
    total_gen = db.execute("SELECT COUNT(*) as n FROM chat_logs").fetchone()["n"]
    db.close()
    return success_response({"total_users": total_users, "total_suggestions": total_sug, "total_generations": total_gen})

def handle_admin_users(event):
    db = get_db()
    rows = db.execute("SELECT id, username, role, status, registered_at FROM users ORDER BY id DESC").fetchall()
    db.close()
    return success_response({"users": [dict(r) for r in rows]})

def handle_admin_update_user(event, user_id):
    data = parse_body(event)
    new_status = data.get("status")
    if not new_status:
        return error_response("Missing 'status' field.", 400)
    
    db = get_db()
    result = db.execute("UPDATE users SET status = ? WHERE id = ? AND role != 'admin'", (new_status, user_id))
    db.commit()
    db.close()
    
    if result.rowcount == 0:
        return error_response("User not found or protected.", 404)
    return success_response({})

def handle_admin_suggestions(event):
    db = get_db()
    rows = db.execute("SELECT id, username, text, reply, timestamp FROM suggestions ORDER BY id DESC").fetchall()
    db.close()
    return success_response({"suggestions": [dict(r) for r in rows]})

def handle_admin_reply_suggestion(event, sug_id):
    data = parse_body(event)
    reply = data.get("reply", "").strip()
    if not reply:
        return error_response("Reply cannot be empty.", 400)
    
    db = get_db()
    result = db.execute("UPDATE suggestions SET reply = ? WHERE id = ?", (reply, sug_id))
    db.commit()
    db.close()
    
    if result.rowcount == 0:
        return error_response("Suggestion not found.", 404)
    return success_response({})

def handle_admin_announcements_get(event):
    db = get_db()
    rows = db.execute("SELECT message, created_at FROM announcements ORDER BY id DESC").fetchall()
    db.close()
    return success_response({"announcements": [r["message"] for r in rows]})

def handle_admin_announcements_post(event):
    data = parse_body(event)
    message = (data.get("message") or "").strip()
    if not message:
        return error_response("Message cannot be empty.", 400)
    
    db = get_db()
    db.execute("INSERT INTO announcements (message) VALUES (?)", (message,))
    db.commit()
    db.close()
    return success_response({})

def handle_init_db(event):
    """Initialize database with tables and seed data."""
    try:
        db = get_db()
        cur = db.cursor()
        
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                status TEXT NOT NULL DEFAULT 'active',
                registered_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                prompt TEXT NOT NULL,
                response TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT DEFAULT 'Anonymous',
                text TEXT NOT NULL,
                reply TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)
        
        # Seed default admin if none exists
        existing = cur.execute("SELECT id FROM users WHERE role='admin' LIMIT 1").fetchone()
        if not existing:
            db.execute(
                "INSERT INTO users (username, password, role, status) VALUES (?, ?, 'admin', 'active')",
                ("admin", hash_pw("admin123"))
            )
            db.commit()
            db.close()
            return success_response({"message": "Database initialized with default admin (admin/admin123)"})
        
        db.close()
        return success_response({"message": "Database already initialized"})
    except Exception as e:
        return error_response(f"Database init failed: {str(e)}", 500)

# ============================================================
# Main Handler (Required by Vercel)
# ============================================================

def handler(event, context):
    """Main Vercel serverless handler."""
    if event.get("httpMethod") == "OPTIONS":
        return cors_preflight()
    
    path = event.get("path", "")
    method = event.get("httpMethod", "GET")
    
    # Ping
    if path == "/api/ping":
        return handle_ping()
    
    # Users
    if "login" in path and method == "POST":
        return handle_users_login(event)
    if "register" in path and method == "POST":
        return handle_users_register(event)
    
    # AI
    if "generate" in path and method == "POST":
        return handle_ai_generate(event)
    if "logs" in path and method == "GET":
        return handle_ai_logs(event)
    
    # Admin
    if "init_db" in path or "init-db" in path:
        return handle_init_db(event)
    if "stats" in path and method == "GET":
        return handle_admin_stats(event)
    if path.rstrip("/").endswith("/users") and method == "GET":
        return handle_admin_users(event)
    
    user_match = re.search(r"/api/admin/users/(\d+)/status", path)
    if user_match and method == "PUT":
        return handle_admin_update_user(event, int(user_match.group(1)))
    
    if "suggestions" in path and "reply" in path and method == "POST":
        sug_match = re.search(r"/api/admin/suggestions/(\d+)/reply", path)
        if sug_match:
            return handle_admin_reply_suggestion(event, int(sug_match.group(1)))
    if "suggestions" in path and method == "GET":
        return handle_admin_suggestions(event)
    
    if "announcements" in path and method == "GET":
        return handle_admin_announcements_get(event)
    if "announcements" in path and method == "POST":
        return handle_admin_announcements_post(event)
    
    return error_response("Not Found", 404)
