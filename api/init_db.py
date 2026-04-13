"""
Database initialization script for Vercel deployment
Run this once after deployment to create tables and seed data
"""
import sqlite3
import hashlib
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "instance" / "fres.db"


def get_db() -> sqlite3.Connection:
    """Get database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_pw(pw: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(pw.encode()).hexdigest()


def init_db():
    """Initialize database with tables and seed data."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT    NOT NULL UNIQUE,
            password     TEXT    NOT NULL,
            role         TEXT    NOT NULL DEFAULT 'user',
            status       TEXT    NOT NULL DEFAULT 'active',
            registered_at TEXT   DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS chat_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            prompt      TEXT    NOT NULL,
            response    TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS suggestions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    DEFAULT 'Anonymous',
            text        TEXT    NOT NULL,
            reply       TEXT,
            timestamp   TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS announcements (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            message     TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        );
    """)

    # Seed a default admin if none exists
    existing = cur.execute("SELECT id FROM users WHERE role='admin' LIMIT 1").fetchone()
    if not existing:
        cur.execute(
            "INSERT INTO users (username, password, role, status) VALUES (?, ?, 'admin', 'active')",
            ("admin", hash_pw("admin123"))
        )
        print("✅ Created default admin user (username: admin, password: admin123)")

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")


if __name__ == "__main__":
    init_db()
