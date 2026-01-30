from __future__ import annotations
from pathlib import Path
from typing import Any

class BaseAdapter:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.readonly = False
        self.data: Any = None

    def set_readonly(self, ro: bool):
        self.readonly = bool(ro)

    def read(self):
        raise NotImplementedError

    def write(self, content: Any):
        if self.readonly:
            raise PermissionError("Adapter is read-only.")
        self.data = content

    def save(self):
        raise NotImplementedError
