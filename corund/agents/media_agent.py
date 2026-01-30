from __future__ import annotations
from .base_agent import BaseAgent

class MediaAgent(BaseAgent):
    def highlight(self, pattern: str):
        return []  # no text highlight for binary

    def analyse(self):
        b = self.adapter.data if isinstance(self.adapter.data, (bytes, bytearray)) else b""
        return {"type": "media", "bytes": len(b)}
