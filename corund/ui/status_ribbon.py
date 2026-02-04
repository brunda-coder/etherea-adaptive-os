from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel

from corund.ui.juicy_button import JuicyChipButton


class StatusRibbon(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("panel", True)
        self.setFixedHeight(46)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        self.focus_timer = QLabel("Focus · 25:00")
        self.workspace_mode = QLabel("Workspace · Calm")
        layout.addWidget(self.focus_timer)
        layout.addWidget(self.workspace_mode)
        layout.addStretch(1)

        layout.addWidget(JuicyChipButton("Notifications"))
        layout.addWidget(JuicyChipButton("Audio"))
        layout.addWidget(JuicyChipButton("Adaptive"))
