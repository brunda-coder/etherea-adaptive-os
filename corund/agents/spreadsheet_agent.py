from __future__ import annotations
from .base_agent import BaseAgent

class SpreadsheetAgent(BaseAgent):
    def highlight(self, pattern: str):
        data = self.adapter.data
        if not isinstance(data, dict) or not pattern:
            return []
        hits = []
        for sheet, rows in data.items():
            for r_i, row in enumerate(rows):
                for c_i, val in enumerate(row):
                    if pattern.lower() in str(val).lower():
                        hits.append((sheet, r_i, c_i))
        return hits

    def analyse(self):
        data = self.adapter.data if isinstance(self.adapter.data, dict) else {}
        return {"type": "spreadsheet", "sheets": list(data.keys())}
