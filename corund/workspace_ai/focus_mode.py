from __future__ import annotations
from typing import Dict


def detect_focus_mode(user_text: str) -> str:
    t = (user_text or "").lower()

    if any(k in t for k in ["regression", "study", "learn", "exam", "math", "notes"]):
        return "study"

    if any(k in t for k in ["code", "bug", "fix", "python", "build", "repo", "commit"]):
        return "coding"

    if any(k in t for k in ["meeting", "call", "zoom", "class", "lecture"]):
        return "meeting"

    if any(k in t for k in ["deep work", "lock in", "focus", "no distractions"]):
        return "deep_work"

    return "study"
