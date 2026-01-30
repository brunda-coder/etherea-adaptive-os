from __future__ import annotations

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Signal


class CommandPalette(QWidget):
    submitted = Signal(str)

    def __init__(self, placeholder: str = "Etherea> type a command (coding mode / save session / continue last session)"):
        super().__init__()
        self.setObjectName("CommandPalette")

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)

        self.btn = QPushButton("Run")

        row = QHBoxLayout(self)
        row.setContentsMargins(8, 8, 8, 8)
        row.setSpacing(8)
        row.addWidget(self.input, 1)
        row.addWidget(self.btn, 0)

        self.btn.clicked.connect(self._emit)
        self.input.returnPressed.connect(self._emit)

    def _emit(self):
        text = (self.input.text() or "").strip()
        if not text:
            return
        self.submitted.emit(text)
        self.input.clear()
