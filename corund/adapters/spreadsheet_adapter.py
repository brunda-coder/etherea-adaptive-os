from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
from .base_adapter import BaseAdapter

class SpreadsheetAdapter(BaseAdapter):
    """
    Edit-ready architecture: stores sheet dict in memory.
    Real XLSX writing can be added using openpyxl later.
    """
    def read(self):
        # placeholder structure
        self.data = {"Sheet1": [["A1","B1"],["A2","B2"]]}

    def save(self):
        # Placeholder: does not write xlsx yet
        # (architecture is ready for adapter-based expansion)
        return
