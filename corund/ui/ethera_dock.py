from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QListWidget, QVBoxLayout

from corund.ui.command_palette import CommandPalette
from corund.ui.juicy_button import JuicyButton, JuicyChipButton


class EtheraDock(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("panel", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Command + Action")
        title.setObjectName("TitleText")
        header.addWidget(title)
        header.addStretch(1)
        layout.addLayout(header)

        self.command_palette = CommandPalette()
        layout.addWidget(self.command_palette)

        self.suggestions = QListWidget()
        self.suggestions.addItems(
            [
                "Start Focus · 25 min",
                "Plan Today",
                "Open Notes",
                "Calm Reset",
            ]
        )
        layout.addWidget(self.suggestions)

        quick = QHBoxLayout()
        quick.addWidget(JuicyButton("Start Focus"))
        quick.addWidget(JuicyButton("Study Mode", variant="secondary"))
        layout.addLayout(quick)

        chips = QHBoxLayout()
        chips.addWidget(JuicyChipButton("Privacy Center"))
        chips.addWidget(JuicyChipButton("Demo Mode"))
        layout.addLayout(chips)

        self.intent_card = QFrame()
        self.intent_card.setProperty("panel", True)
        intent_layout = QVBoxLayout(self.intent_card)
        intent_layout.setContentsMargins(12, 12, 12, 12)
        intent_layout.setSpacing(6)
        intent_title = QLabel("Intent Result")
        intent_title.setStyleSheet("font-weight:600;")
        intent_desc = QLabel("Ready to route commands and show context.")
        intent_desc.setWordWrap(True)
        intent_desc.setStyleSheet("color:#9aa0c6;")
        intent_layout.addWidget(intent_title)
        intent_layout.addWidget(intent_desc)
        layout.addWidget(self.intent_card)
