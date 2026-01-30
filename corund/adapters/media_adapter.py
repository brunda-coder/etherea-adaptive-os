from __future__ import annotations
from pathlib import Path
from typing import Any
from .base_adapter import BaseAdapter

class MediaAdapter(BaseAdapter):
    def read(self):
        if self.path.exists():
            self.data = self.path.read_bytes()
        else:
            self.data = b""

    def write(self, content: Any):
        if self.readonly:
            raise PermissionError("Read-only.")
        if not isinstance(content, (bytes, bytearray)):
            raise TypeError("MediaAdapter expects bytes.")
        self.data = bytes(content)

    def save(self):
        if self.readonly:
            raise PermissionError("Read-only.")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(self.data or b"")
