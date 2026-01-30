from __future__ import annotations
from typing import Any, List, Tuple

class BaseAgent:
    def __init__(self, adapter: Any):
        self.adapter = adapter

    def highlight(self, pattern: str) -> List[Tuple[int,int]]:
        # simple highlight in text
        data = self.adapter.data
        if not isinstance(data, str) or not pattern:
            return []
        res = []
        start = 0
        p = pattern.lower()
        low = data.lower()
        while True:
            i = low.find(p, start)
            if i == -1:
                break
            res.append((i, i+len(pattern)))
            start = i + len(pattern)
        return res

    def analyse(self):
        return {"type": "base", "info": "No analysis implemented"}
