# core/memory_store.py
"""
Memory Store for Etherea
- Persistent storage of session state, outputs, visuals, and emotional data
- Supports real-time, dynamic, multi-modal outputs
"""

import os
import json
import base64
try:
    import requests
except Exception:
    requests = None  # optional on Termux/CI
from corund.utils import ensure_folder, debug_print
from corund.database import db


class MemoryStore:
    def __init__(self):
        # Leverage the global 'db' instance for SQLite persistence
        self.db = db
        debug_print("MemoryStore", "Initialized with SQLite LTM")

    # --- LTM Methods ---
    def add_to_ltm(self, content: str, memory_type: str = "general", embedding=None):
        """Add a persistent memory with optional embedding"""
        if not content:
            debug_print("MemoryStore",
                        "Warning: Empty content not added to LTM")
            return
        self.db.add_memory(content, memory_type, embedding)
        debug_print("MemoryStore", f"Added to LTM: {content[:30]}...")

    def search_ltm(self, query_embedding, limit: int = 5):
        """Search LTM using semantic similarity"""
        if query_embedding is None:
            debug_print("MemoryStore",
                        "No embedding provided, returning recent memories")
        return self.db.search_memories(query_embedding, limit)

    def get_history(self, limit: int = 5):
        """Get recent LTM entries"""
        return self.db.get_recent_memories(limit)

    # --- Profile / Preferences ---
    def update_preference(self, key: str, value: str):
        if not key:
            debug_print("MemoryStore",
                        "Warning: Empty key ignored in update_preference")
            return
        self.db.set_preference(key, value)

    def get_all_preferences(self):
        return self.db.get_profile_context()

    # --- Emotional State ---
    def update_emotion(self, emotion_dict: dict):
        """Store emotional context in profile"""
        if not isinstance(emotion_dict, dict):
            debug_print("MemoryStore",
                        f"update_emotion: Invalid type {type(emotion_dict)}")
            return
        self.update_preference("last_emotion", json.dumps(emotion_dict))

    def get_emotion(self):
        """Retrieve last known emotional state"""
        pref = self.db.get_profile_context()
        raw = pref.get("last_emotion")
        if raw:
            try:
                return json.loads(raw)
            except Exception as e:
                debug_print("MemoryStore",
                            f"get_emotion JSON decode error: {e}")
        return {"tone": "neutral", "intensity": 0.5}

    # --- Image Handling ---
    def save_image_from_url(self, key: str, url: str, timeout: int = 5) -> bool:
        """
        Fetch image from URL, convert to base64, and store in preferences.
        Returns True if successful, False on error.
        """
        if not key or not url:
            debug_print("MemoryStore", "save_image_from_url: key or URL empty")
            return False

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            b64 = base64.b64encode(response.content).decode("utf-8")
            self.update_preference(f"img_{key}", b64)
            return True
        except Exception as e:
            debug_print("MemoryStore", f"save_image_from_url error: {e}")
            return False
