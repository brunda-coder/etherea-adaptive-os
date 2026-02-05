from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QProcess, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from corund.app_runtime import user_data_dir
from corund.runtime_diagnostics import DiagnosticReport, RuntimeDiagnostics


class RecoveryScreen(QDialog):
    def __init__(
        self,
        diagnostics: RuntimeDiagnostics,
        report: DiagnosticReport,
        report_url: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.diagnostics = diagnostics
        self.report = report
        self.report_url = report_url
        self.setWindowTitle("Etherea Recovery Screen")
        self.setMinimumSize(720, 420)

        layout = QVBoxLayout(self)
        title = QLabel("We ran into a startup issue.")
        title.setStyleSheet("font-size:18px; font-weight:700;")
        layout.addWidget(title)

        summary = QLabel("Etherea entered Recovery Mode. You can restart in Safe Mode or report diagnostics.")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlainText(self._build_details_text())
        layout.addWidget(self.details, 1)

        btn_row = QHBoxLayout()
        self.safe_btn = QPushButton("Restart in Safe Mode")
        self.logs_btn = QPushButton("Open Logs Folder")
        self.copy_btn = QPushButton("Copy Report")
        self.save_btn = QPushButton("Save Report")
        self.report_btn = QPushButton("Report Issue")
        self.exit_btn = QPushButton("Exit")
        btn_row.addWidget(self.safe_btn)
        btn_row.addWidget(self.logs_btn)
        btn_row.addWidget(self.copy_btn)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.report_btn)
        btn_row.addWidget(self.exit_btn)
        layout.addLayout(btn_row)

        self.safe_btn.clicked.connect(self._restart_safe_mode)
        self.logs_btn.clicked.connect(self._open_logs)
        self.copy_btn.clicked.connect(self._copy_report)
        self.save_btn.clicked.connect(self._save_report)
        self.report_btn.clicked.connect(self._report_issue)
        self.exit_btn.clicked.connect(self.reject)

    def _build_details_text(self) -> str:
        return self._build_report_text(include_full_log=False)

    def _build_report_text(self, *, include_full_log: bool) -> str:
        lines = ["Errors:"]
        lines.extend(f"- {err}" for err in self.report.errors)
        if self.report.warnings:
            lines.append("")
            lines.append("Warnings:")
            lines.extend(f"- {warn}" for warn in self.report.warnings)
        lines.append("")
        lines.append("Diagnostics:")
        lines.append(self.diagnostics.diagnostics_text(self.report))
        if include_full_log:
            lines.append("")
            lines.append("Full Log (etherea.log):")
            log_contents = self.diagnostics.log_contents()
            lines.append(log_contents if log_contents else "(log file unavailable)")
        return "\n".join(lines)

    def _restart_safe_mode(self) -> None:
        args = [arg for arg in sys.argv[1:] if arg not in {"--safe-mode"}]
        args.append("--safe-mode")
        QProcess.startDetached(sys.executable, args)
        QApplication.instance().quit()

    def _open_logs(self) -> None:
        logs_dir = user_data_dir() / "logs"
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(logs_dir)))

    def _copy_report(self) -> None:
        clipboard = QApplication.instance().clipboard()
        clipboard.setText(self._build_report_text(include_full_log=False))

    def _save_report(self) -> None:
        default_name = str(user_data_dir() / "etherea_report.txt")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Diagnostic Report",
            default_name,
            "Text Files (*.txt);;All Files (*)",
        )
        if not file_path:
            return
        Path(file_path).write_text(
            self._build_report_text(include_full_log=True),
            encoding="utf-8",
        )

    def _report_issue(self) -> None:
        QDesktopServices.openUrl(QUrl(self.report_url))
