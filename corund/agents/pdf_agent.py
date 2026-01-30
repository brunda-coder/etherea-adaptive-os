from __future__ import annotations
from .base_agent import BaseAgent

class PDFAgent(BaseAgent):
    def analyse(self):
        data = self.adapter.data if isinstance(self.adapter.data, dict) else {}
        return {"type": "pdf", "keys": list(data.keys())}
