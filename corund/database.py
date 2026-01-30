import sqlite3
import os
import json
try:
    import numpy as np
except Exception:
    np = None  # optional on Termux/CI
from datetime import datetime


class Database:
    def __init__(self, db_path="data/etherea.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        # Ensure connection uses check_same_thread=False safely
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")  # safe default
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Memories Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                type TEXT DEFAULT 'general',
                embedding BLOB,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User Profile Table (Key-Value)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        self.conn.commit()

    def add_memory(self, content: str, memory_type: str = "general", embedding=None):
        cursor = self.conn.cursor()
        # Only convert embedding if not None
        emb_blob = None
        if embedding is not None:
            try:
                emb_array = np.array(embedding, dtype=np.float32)
                emb_blob = sqlite3.Binary(emb_array.tobytes())
            except Exception as e:
                print(f"Failed to convert embedding to blob: {e}")
                emb_blob = None
        cursor.execute(
            "INSERT INTO memories (content, type, embedding) VALUES (?, ?, ?)",
            (content, memory_type, emb_blob)
        )
        self.conn.commit()

    def search_memories(self, query_embedding, limit: int = 5):
        """
        Search memories using cosine similarity of embeddings.
        """
        if query_embedding is None:
            return self.get_recent_memories(limit)

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT content, embedding FROM memories WHERE embedding IS NOT NULL")
        rows = cursor.fetchall()

        if not rows:
            return []

        search_vec = np.array(query_embedding, dtype=np.float32)
        results = []

        for content, emb_blob in rows:
            try:
                emb = np.frombuffer(emb_blob, dtype=np.float32)
                # Cosine similarity: (A . B) / (||A|| * ||B||)
                norm = np.linalg.norm(search_vec) * np.linalg.norm(emb) + 1e-9
                sim = np.dot(search_vec, emb) / norm
                results.append((content, sim))
            except Exception as e:
                print(f"Failed to compute similarity for a memory: {e}")

        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        return [res[0] for res in results[:limit]]

    def get_recent_memories(self, limit: int = 5):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT content FROM memories ORDER BY created_at DESC LIMIT ?", (limit,))
        return [row[0] for row in cursor.fetchall()]

    def set_preference(self, key: str, value: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)",
            (key, value)
        )
        self.conn.commit()

    def get_profile_context(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT key, value FROM user_profile")
        rows = cursor.fetchall()
        if rows is None:
            return {}
        return {row[0]: row[1] for row in rows}


# Global Instance
db = Database()
