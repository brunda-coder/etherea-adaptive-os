from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List
import json
import time


DEFAULT_SESSION_FILE = Path("workspace/.etherea_last_session.json")


@dataclass
class SessionSnapshot:
    saved_at: float
    open_files: List[Dict[str, Any]]  # [{path, sealed}]
    notes: str = ""


def save_snapshot(snapshot: Dict[str, Any], session_file: Path = DEFAULT_SESSION_FILE) -> Path:
    session_file.parent.mkdir(parents=True, exist_ok=True)
    snapshot = dict(snapshot or {})
    snapshot["saved_at"] = float(time.time())
    session_file.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return session_file


def load_snapshot(session_file: Path = DEFAULT_SESSION_FILE) -> Dict[str, Any]:
    if not session_file.exists():
        return {}
    try:
        return json.loads(session_file.read_text(encoding="utf-8"))
    except Exception:
        return {}
