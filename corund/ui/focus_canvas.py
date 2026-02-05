from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from corund.ui.aurora_ring_widget import AuroraRingWidget
from corund.ui.juicy_button import JuicyButton


class FocusCanvas(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("panel", True)
        self.setObjectName("AuroraCanvas")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Focus Canvas")
        title.setObjectName("TitleText")
        subtitle = QLabel("Keep the stage calm. Two cards max.")
        subtitle.setObjectName("CandySubtitle")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(subtitle)
        layout.addLayout(header)

        self.ring = AuroraRingWidget(mode="expanded")
        self.ring.setMinimumHeight(180)
        layout.addWidget(self.ring)

        cards_row_one = QHBoxLayout()
        self._add_card(cards_row_one, "Missions", "3 quests · 1 priority")
        self._add_card(cards_row_one, "Focus Streak", "4 days · 25:00 sprint")
        layout.addLayout(cards_row_one)

        cards_row_two = QHBoxLayout()
        self._add_card(cards_row_two, "Mood", "Calm · breathing reset")
        self._add_card(cards_row_two, "Quick Actions", "Open workspace · Capture note")
        layout.addLayout(cards_row_two)

    def _add_card(self, layout: QHBoxLayout, title: str, desc: str) -> None:
        card = QFrame()
        card.setProperty("panel", True)
        card.setObjectName("CandyCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(6)
        label = QLabel(title)
        label.setStyleSheet("font-weight:600;")
        detail = QLabel(desc)
        detail.setStyleSheet("color:#9aa0c6;")
        action = JuicyButton("Open", variant="ghost")
        card_layout.addWidget(label)
        card_layout.addWidget(detail)
        card_layout.addStretch(1)
        card_layout.addWidget(action, alignment=Qt.AlignLeft)
        layout.addWidget(card, 1)
