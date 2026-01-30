from __future__ import annotations
from .base_agent import BaseAgent

class DocumentAgent(BaseAgent):
    def analyse(self):
        txt = self.adapter.data if isinstance(self.adapter.data, str) else ""
        words = txt.split()
        return {"type": "document", "words": len(words), "preview": " ".join(words[:40])}
