from __future__ import annotations
from .base_agent import BaseAgent

class CodeAgent(BaseAgent):
    def analyse(self):
        txt = self.adapter.data if isinstance(self.adapter.data, str) else ""
        lines = txt.splitlines()
        return {"type": "code", "lines": len(lines)}
