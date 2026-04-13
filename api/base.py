"""
FRES API - Base utilities for Vercel serverless functions
"""
import json
import os
import sqlite3
from pathlib import Path
from http.cookies import SimpleCookie

# Database path
DB_PATH = Path(__file__).resolve().parent.parent / "instance" / "fres.db"


def get_db() -> sqlite3.Connection:
    """Get database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_pw(pw: str) -> str:
    """Hash password using SHA-256."""
    import hashlib
    return hashlib.sha256(pw.encode()).hexdigest()


def success_response(data, status=200):
    """Create a success JSON response."""
    body = json.dumps({"success": True, **data}).encode()
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept",
        },
        "body": body.decode()
    }


def error_response(message, status=400):
    """Create an error JSON response."""
    body = json.dumps({"success": False, "error": message}).encode()
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept",
        },
        "body": body.decode()
    }


def parse_body(event):
    """Parse request body from Vercel event."""
    try:
        body_str = event.get("body", "{}")
        if isinstance(body_str, str):
            return json.loads(body_str)
        return body_str
    except (json.JSONDecodeError, TypeError):
        return {}


def cors_preflight(event):
    """Handle CORS preflight requests."""
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept",
        },
        "body": ""
    }
