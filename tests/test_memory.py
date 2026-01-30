import os
import sqlite3
try:
    import numpy as np
except Exception:
    np = None  # optional on Termux/CI
import pytest
from corund.database import Database
from corund.memory_store import MemoryStore

DB_TEST_PATH = "data/test_etherea.db"


@pytest.fixture
def db():
    if os.path.exists(DB_TEST_PATH):
        os.remove(DB_TEST_PATH)
    database = Database(db_path=DB_TEST_PATH)
    yield database
    database.conn.close()
    if os.path.exists(DB_TEST_PATH):
        os.remove(DB_TEST_PATH)


def test_database_persistence(db):
    db.add_memory("Test memory content", "test")
    memories = db.get_recent_memories(1)
    assert len(memories) == 1
    assert memories[0] == "Test memory content"


def test_semantic_search(db):
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [0.0, 1.0, 0.0]

    db.add_memory("Vector 1 Memory", "test", embedding=vec1)
    db.add_memory("Vector 2 Memory", "test", embedding=vec2)

    # Search with something close to vec1
    results = db.search_memories([0.9, 0.1, 0.0], limit=1)
    assert results[0] == "Vector 1 Memory"


def test_memory_store_integration(db):
    # Mock global db for MemoryStore if needed, or just test its methods
    store = MemoryStore()
    store.db = db  # Injection for testing

    store.add_to_ltm("Persistent context", "context")
    history = store.get_history()
    assert "Persistent context" in history
