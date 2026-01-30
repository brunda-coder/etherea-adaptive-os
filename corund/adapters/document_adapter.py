from __future__ import annotations
from pathlib import Path
from typing import Any
from .base_adapter import BaseAdapter

class DocumentAdapter(BaseAdapter):
    def read(self):
        if self.path.exists():
            self.data = self.path.read_text(encoding="utf-8", errors="ignore")
        else:
            self.data = ""

    def save(self):
        if self.readonly:
            raise PermissionError("Read-only.")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(str(self.data), encoding="utf-8")
