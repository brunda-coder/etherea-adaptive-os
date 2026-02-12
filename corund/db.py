from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Iterable

from corund.app_runtime import user_data_dir

_DB_LOCK = threading.Lock()
_DB_PATH: Path | None = None


def db_path() -> Path:
    global _DB_PATH
    if _DB_PATH is None:
        root = user_data_dir("EthereaOS")
        _DB_PATH = root / "etherea.sqlite3"
    return _DB_PATH


def connect() -> sqlite3.Connection:
    """
    Returns a sqlite3 connection with sane defaults.
    - WAL for concurrency
    - foreign keys enabled
    """
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30, isolation_level=None)  # autocommit
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA busy_timeout=30000;")
    return conn


def _exec_many(conn: sqlite3.Connection, stmts: Iterable[str]) -> None:
    cur = conn.cursor()
    for s in stmts:
        cur.execute(s)
    cur.close()


def migrate() -> None:
    """
    Idempotent migrations. Safe to call on every startup.
    """
    with _DB_LOCK:
        conn = connect()
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations ("
                "  id INTEGER PRIMARY KEY,"
                "  name TEXT UNIQUE NOT NULL,"
                "  applied_at TEXT DEFAULT (datetime('now'))"
                ");"
            )

            # Migration 001: sessions/events/decisions/user_controls
            conn.execute(
                "INSERT OR IGNORE INTO schema_migrations(name) VALUES ('001_core_tables');"
            )

            _exec_many(
                conn,
                [
                    # sessions
                    """
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        started_at TEXT NOT NULL DEFAULT (datetime('now')),
                        ended_at   TEXT,
                        workspace  TEXT,
                        privacy_mode TEXT DEFAULT 'normal'
                    );
                    """,
                    # events
                    """
                    CREATE TABLE IF NOT EXISTS events (
                        event_id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        source TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT (datetime('now')),
                        payload_json TEXT NOT NULL
                    );
                    """,
                    "CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);",
                    "CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at);",
                    # agent decisions
                    """
                    CREATE TABLE IF NOT EXISTS agent_decisions (
                        decision_id TEXT PRIMARY KEY,
                        created_at TEXT NOT NULL DEFAULT (datetime('now')),
                        agent TEXT NOT NULL,
                        workspace TEXT,
                        tool_name TEXT NOT NULL,
                        args_json TEXT NOT NULL,
                        reason TEXT NOT NULL,
                        executed INTEGER NOT NULL DEFAULT 0,
                        execution_result TEXT,
                        blocked_by_privacy INTEGER NOT NULL DEFAULT 0
                    );
                    """,
                    "CREATE INDEX IF NOT EXISTS idx_decisions_created ON agent_decisions(created_at);",
                    "CREATE INDEX IF NOT EXISTS idx_decisions_tool ON agent_decisions(tool_name);",
                    # user controls (privacy + learning)
                    """
                    CREATE TABLE IF NOT EXISTS user_controls (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                    );
                    """,
                ],
            )
        finally:
            conn.close()
