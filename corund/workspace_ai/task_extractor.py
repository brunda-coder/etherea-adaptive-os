from __future__ import annotations
import re
from typing import List, Dict


TODO_PATTERNS = [
    r"\bTODO\b[:\-]?\s*(.+)",
    r"\bTo do\b[:\-]?\s*(.+)",
    r"\bTask\b[:\-]?\s*(.+)",
    r"\bFix\b[:\-]?\s*(.+)",
    r"\bNeed to\b\s*(.+)"
]


def extract_tasks(text: str) -> List[Dict[str, str]]:
    tasks = []
    s = text or ""

    for pat in TODO_PATTERNS:
        for m in re.finditer(pat, s, flags=re.IGNORECASE):
            item = m.group(1).strip()
            if item:
                tasks.append({"task": item})

    # Bullet items that look like tasks
    for line in s.splitlines():
        line = line.strip()
        if line.startswith(("-", "*")) and len(line) > 6:
            tasks.append({"task": line.lstrip("-* ").strip()})

    # Deduplicate
    seen = set()
    out = []
    for t in tasks:
        key = t["task"].lower()
        if key not in seen:
            seen.add(key)
            out.append(t)

    return out
