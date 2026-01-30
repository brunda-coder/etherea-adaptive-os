# setup_data.py
"""
Setup script for Etherea databases.
- Creates etherea.db and openai_logs.db if missing
- Creates tables
- Seeds default admin user and sample log entry
"""

import sqlite3
from pathlib import Path
from datetime import datetime

# ------------------ Paths ------------------
DB_PATH = Path("data")
DB_PATH.mkdir(exist_ok=True)

ETHEREA_DB = DB_PATH / "etherea.db"
OPENAI_DB = DB_PATH / "openai_logs.db"

# ------------------ ETHEREA DB ------------------
with sqlite3.connect(ETHEREA_DB) as eth_conn:
    eth_cursor = eth_conn.cursor()

    # Users table
    eth_cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Sessions table
    eth_cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        started_at DATETIME,
        ended_at DATETIME,
        focus_level INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    # Events table
    eth_cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        type TEXT,
        details TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(session_id) REFERENCES sessions(id)
    );
    """)

    # Seed default admin if none exists
    eth_cursor.execute("SELECT COUNT(*) FROM users;")
    if eth_cursor.fetchone()[0] == 0:
        eth_cursor.execute(
            "INSERT INTO users (name, role) VALUES (?, ?)",
            ("DefaultUser", "admin")
        )
        print("[SUCCESS] Default admin user created.")

# ------------------ OPENAI LOGS DB ------------------
with sqlite3.connect(OPENAI_DB) as openai_conn:
    openai_cursor = openai_conn.cursor()

    # API logs
    openai_cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        prompt TEXT,
        response TEXT,
        tokens_used INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # API errors
    openai_cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_errors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        error_message TEXT,
        status_code INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Seed sample log if empty
    openai_cursor.execute("SELECT COUNT(*) FROM api_logs;")
    if openai_cursor.fetchone()[0] == 0:
        openai_cursor.execute(
            "INSERT INTO api_logs (user_id, prompt, response, tokens_used) VALUES (?, ?, ?, ?)",
            ("DefaultUser", "Hello AI", "Hello human!", 5)
        )
        print("[SUCCESS] Sample API log created.")

print("[DONE] Databases setup complete. Ready to rock.")
