from __future__ import annotations
from pathlib import Path
from typing import Type

from .base_adapter import BaseAdapter
from .code_adapter import CodeAdapter
from .document_adapter import DocumentAdapter
from .spreadsheet_adapter import SpreadsheetAdapter
from .pdf_adapter import PDFAdapter
from .media_adapter import MediaAdapter

ADAPTERS = {
    # code
    ".py": CodeAdapter,
    ".js": CodeAdapter,
    ".html": CodeAdapter,
    ".css": CodeAdapter,
    ".json": CodeAdapter,
    ".md": CodeAdapter,

    # docs
    ".txt": DocumentAdapter,
    ".docx": DocumentAdapter,  # foundation (real docx later)

    # sheets
    ".xlsx": SpreadsheetAdapter,

    # pdf
    ".pdf": PDFAdapter,

    # media
    ".png": MediaAdapter,
    ".jpg": MediaAdapter,
    ".jpeg": MediaAdapter,
    ".webp": MediaAdapter,
    ".mp3": MediaAdapter,
    ".wav": MediaAdapter,
    ".mp4": MediaAdapter,
}

def get_adapter_for_path(path: Path) -> BaseAdapter:
    ext = path.suffix.lower()
    cls: Type[BaseAdapter] = ADAPTERS.get(ext, DocumentAdapter)
    return cls(path)
