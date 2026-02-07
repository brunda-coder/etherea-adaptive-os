from __future__ import annotations

import json

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTextEdit,
)

from corund.agent_registry import AgentRegistry


class DemoModePanel(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("panel", True)
        self.registry = AgentRegistry()

        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        title = QLabel("Agent Works")
        title.setObjectName("TitleText")
        self.status = QLabel("Idle")
        header.addWidget(title); header.addStretch(1); header.addWidget(self.status)
        layout.addLayout(header)

        self.task_input = QLineEdit("AI in Education")
        self.task_input.setPlaceholderText("Requested task topic/path")
        layout.addWidget(self.task_input)

        btns = QHBoxLayout()
        self.btn_ppt = QPushButton("Create PPT Plan")
        self.btn_pdf = QPushButton("Summarize PDF")
        self.btn_notes = QPushButton("Generate Notes")
        self.btn_pause = QPushButton("Safety Pause")
        self.btn_cancel = QPushButton("Cancel")
        for b in (self.btn_ppt, self.btn_pdf, self.btn_notes, self.btn_pause, self.btn_cancel):
            btns.addWidget(b)
        layout.addLayout(btns)

        self.requested_task = QLabel("Requested task: -")
        self.plan_list = QListWidget()
        self.execution_list = QListWidget()
        self.output = QTextEdit(); self.output.setReadOnly(True)
        layout.addWidget(self.requested_task)
        layout.addWidget(QLabel("Plan")); layout.addWidget(self.plan_list)
        layout.addWidget(QLabel("Execution steps")); layout.addWidget(self.execution_list)
        layout.addWidget(self.output)

        self.btn_ppt.clicked.connect(lambda: self._run("ppt"))
        self.btn_pdf.clicked.connect(lambda: self._run("pdf"))
        self.btn_notes.clicked.connect(lambda: self._run("notes"))
        self.btn_pause.clicked.connect(lambda: self.status.setText("Paused"))
        self.btn_cancel.clicked.connect(self._cancel)

    def _run(self, kind: str) -> None:
        self.status.setText("Running")
        query = self.task_input.text().strip() or "demo"
        if kind == "ppt":
            result = self.registry.create_ppt(query)
        elif kind == "pdf":
            result = self.registry.summarize_pdf(query)
        else:
            result = self.registry.generate_notes(query)
        self._render(result)
        self.status.setText("Done")

    def _render(self, result) -> None:
        self.requested_task.setText(f"Requested task: {result.task}")
        self.plan_list.clear(); self.plan_list.addItems(result.plan)
        self.execution_list.clear(); self.execution_list.addItems(result.execution_steps)
        self.output.setPlainText(json.dumps(result.output, indent=2))

    def _cancel(self) -> None:
        self.status.setText("Cancelled")
        self.plan_list.clear(); self.execution_list.clear(); self.output.clear()
