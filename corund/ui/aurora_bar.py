from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QFrame

from corund.ui.aurora_ring_widget import AuroraRingWidget


class AuroraBar(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("AuroraBar")
        self.setProperty("panel", True)
        self.setFixedHeight(54)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        self.ring = AuroraRingWidget(mode="mini")
        self.ring.setFixedSize(36, 36)
        layout.addWidget(self.ring)

        self.time_icon = QLabel("🌙")
        self.time_icon.setAlignment(Qt.AlignCenter)
        self.time_icon.setFixedWidth(32)
        layout.addWidget(self.time_icon)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search or command…  (Ctrl+K)")
        layout.addWidget(self.search, 1)

        self.status = QLabel("Aurora · Calm")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFixedWidth(120)
        layout.addWidget(self.status)
