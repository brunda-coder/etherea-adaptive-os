from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget, QTextEdit

from corund.ui.juicy_button import JuicyButton
from corund.resource_manager import ResourceManager


class DemoModePanel(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("panel", True)
        script_resolved = ResourceManager.resolve_asset("assets/demo/demo_script_01.json")
        self.script_path = Path(script_resolved) if script_resolved else None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Demo Mode")
        title.setObjectName("TitleText")
        self.status = QLabel("Idle")
        self.status.setStyleSheet("color:#8a90b8;")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.status)
        layout.addLayout(header)

        self.steps = QListWidget()
        self.steps.setMinimumHeight(140)
        layout.addWidget(self.steps)

        controls = QHBoxLayout()
        self.start_btn = JuicyButton("Start Demo")
        self.next_btn = JuicyButton("Next", variant="secondary")
        self.prev_btn = JuicyButton("Back", variant="secondary")
        controls.addWidget(self.start_btn)
        controls.addWidget(self.prev_btn)
        controls.addWidget(self.next_btn)
        layout.addLayout(controls)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Demo script JSON will appear here.")
        layout.addWidget(self.editor, 1)

        self.start_btn.clicked.connect(self._start)
        self.next_btn.clicked.connect(self._next)
        self.prev_btn.clicked.connect(self._prev)

        self._load_script()

    def _load_script(self) -> None:
        if self.script_path is None or not self.script_path.exists():
            self.status.setText("Demo assets not installed")
            self.steps.hide()
            self.start_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.prev_btn.setEnabled(False)
            self.editor.setPlainText('{\n  "message": "Demo assets not installed"\n}')
            return
        self.editor.setPlainText(self.script_path.read_text(encoding="utf-8"))
        try:
            data = json.loads(self.editor.toPlainText())
        except json.JSONDecodeError:
            return
        steps = data.get("steps", [])
        self.steps.clear()
        for step in steps:
            title = step.get("title", "Step")
            moment = step.get("moment", "")
            self.steps.addItem(f"{title} · {moment}")

    def _start(self) -> None:
        self.status.setText("Active")
        if self.steps.count() > 0:
            self.steps.setCurrentRow(0)

    def _next(self) -> None:
        row = self.steps.currentRow()
        if row < self.steps.count() - 1:
            self.steps.setCurrentRow(row + 1)

    def _prev(self) -> None:
        row = self.steps.currentRow()
        if row > 0:
            self.steps.setCurrentRow(row - 1)
