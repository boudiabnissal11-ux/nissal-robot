# ============================================================
# Ghost DB — قاعدة بيانات الشبح
# SQLite — أساس يكبر معنا لاحقاً
# ============================================================

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = "data/ghost.db"


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """إنشاء الجداول إذا لم تكن موجودة"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            platform_user_id TEXT NOT NULL,
            name TEXT,
            is_owner INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(platform, platform_user_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            platform TEXT,
            sender TEXT,
            message TEXT,
            response_type TEXT,
            lang TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            channel_name TEXT,
            plan TEXT,
            status TEXT DEFAULT 'active',
            started_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT,
            payment_method TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS learned_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            content TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def get_or_create_user(platform, platform_user_id, name=None, is_owner=False):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE platform=? AND platform_user_id=?",
        (platform, platform_user_id)
    )
    row = cur.fetchone()

    if row:
        conn.close()
        return dict(row)

    cur.execute(
        "INSERT INTO users (platform, platform_user_id, name, is_owner) VALUES (?, ?, ?, ?)",
        (platform, platform_user_id, name, int(is_owner))
    )
    conn.commit()

    user_id = cur.lastrowid
    conn.close()
    return {"id": user_id, "platform": platform, "platform_user_id": platform_user_id,
            "name": name, "is_owner": int(is_owner)}


def save_message(user_id, platform, sender, message, response_type="text", lang=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (user_id, platform, sender, message, response_type, lang) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, platform, sender, message, response_type, lang)
    )
    conn.commit()
    conn.close()


def add_subscription(user_id, channel_name, plan, days, payment_method=None):
    expires_at = (datetime.now() + timedelta(days=days)).isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO subscriptions (user_id, channel_name, plan, status, expires_at, payment_method)
           VALUES (?, ?, ?, 'active', ?, ?)""",
        (user_id, channel_name, plan, expires_at, payment_method)
    )
    conn.commit()
    conn.close()


def get_expired_subscriptions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM subscriptions WHERE status='active' AND expires_at < ?",
        (datetime.now().isoformat(),)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_subscription_expired(subscription_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE subscriptions SET status='expired' WHERE id=?",
        (subscription_id,)
    )
    conn.commit()
    conn.close()
