from __future__ import annotations
from pathlib import Path
from typing import Any, List
from .base_adapter import BaseAdapter

class PDFAdapter(BaseAdapter):
    """
    Adapter-based PDF handling foundation:
    - open (extract placeholder)
    - annotate (store notes)
    - rebuild workflow (future)
    """
    def read(self):
        self.data = {"pages": [], "annotations": []}

    def write(self, content: Any):
        if self.readonly:
            raise PermissionError("Read-only.")
        self.data = content

    def save(self):
        # future: rebuild PDF
        return
