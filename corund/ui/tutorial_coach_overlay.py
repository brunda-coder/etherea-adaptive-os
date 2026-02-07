from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from corund.tutorial_overlay import TutorialOverlayStateMachine


class TutorialCoachOverlay(QFrame):
    completed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("TutorialCoachOverlay")
        self.setStyleSheet("QFrame#TutorialCoachOverlay{background:rgba(10,12,26,215); border:1px solid #6f75ac; border-radius:12px;}")
        self.machine = TutorialOverlayStateMachine()
        self.settings_path = Path.home() / ".etherea_tutorial.json"

        layout = QVBoxLayout(self)
        self.title = QLabel("Tutorial")
        self.text = QLabel("")
        self.text.setWordWrap(True)
        self.target = QLabel("")
        layout.addWidget(self.title)
        layout.addWidget(self.text)
        layout.addWidget(self.target)

        btns = QHBoxLayout()
        self.back = QPushButton("Back")
        self.next = QPushButton("Next")
        self.skip = QPushButton("Skip")
        btns.addWidget(self.back)
        btns.addWidget(self.next)
        btns.addWidget(self.skip)
        layout.addLayout(btns)

        self.back.clicked.connect(self._on_back)
        self.next.clicked.connect(self._on_next)
        self.skip.clicked.connect(self._on_skip)
        self.setVisible(False)

    def start(self) -> None:
        if self.is_completed():
            return
        step = self.machine.start()
        self._render(step)
        self.setVisible(True)

    def _on_back(self) -> None:
        self.machine.index = max(0, self.machine.index - 1)
        self._render(self.machine.current())

    def _on_next(self) -> None:
        if self.machine.index >= len(self.machine.steps) - 1:
            self._finish()
            return
        step = self.machine.next()
        self._render(step)

    def _on_skip(self) -> None:
        self._finish()

    def _finish(self) -> None:
        self.setVisible(False)
        self._persist_completed(True)
        self.completed.emit()

    def _render(self, step) -> None:
        self.title.setText(f"{step.title}")
        self.text.setText(step.instruction)
        self.target.setText(f"Highlight: {step.target}")

    def is_completed(self) -> bool:
        if not self.settings_path.exists():
            return False
        try:
            return bool(json.loads(self.settings_path.read_text()).get("tutorial_completed"))
        except Exception:
            return False

    def _persist_completed(self, done: bool) -> None:
        self.settings_path.write_text(json.dumps({"tutorial_completed": done}, indent=2), encoding="utf-8")
