from __future__ import annotations
from typing import Any

from corund.adapters.code_adapter import CodeAdapter
from corund.adapters.document_adapter import DocumentAdapter
from corund.adapters.spreadsheet_adapter import SpreadsheetAdapter
from corund.adapters.pdf_adapter import PDFAdapter
from corund.adapters.media_adapter import MediaAdapter

from .code_agent import CodeAgent
from .document_agent import DocumentAgent
from .spreadsheet_agent import SpreadsheetAgent
from .pdf_agent import PDFAgent
from .media_agent import MediaAgent

def get_agent_for_adapter(adapter: Any):
    if isinstance(adapter, CodeAdapter):
        return CodeAgent(adapter)
    if isinstance(adapter, SpreadsheetAdapter):
        return SpreadsheetAgent(adapter)
    if isinstance(adapter, PDFAdapter):
        return PDFAgent(adapter)
    if isinstance(adapter, MediaAdapter):
        return MediaAgent(adapter)
    return DocumentAgent(adapter)
