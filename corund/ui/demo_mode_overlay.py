from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class DemoModeOverlay(QFrame):
    def __init__(self, steps: list[dict[str, str]] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.steps = steps or []
        self.current_index = 0
        self.active = False

        self.setObjectName("DemoModeOverlay")
        self.setStyleSheet(
            "QFrame#DemoModeOverlay { background:#0f111d; border:1px solid #20243a; "
            "border-radius:16px; padding:12px; }"
            "QLabel { color:#e6e7ff; }"
            "QPushButton { background:#202545; border:none; border-radius:10px; padding:6px 12px; "
            "color:#e6e7ff; }"
            "QPushButton:disabled { color:#6f7392; background:#1a1d34; }"
            "QPushButton#PrimaryButton { background:#5a6bff; font-weight:600; }"
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        header = QHBoxLayout()
        self.title = QLabel("Demo Mode · Guided Tour")
        self.title.setStyleSheet("font-size:15px; font-weight:600;")
        self.status = QLabel("Idle")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFixedHeight(24)
        self.status.setStyleSheet(
            "background:#1c2036; border-radius:12px; padding:0 10px; font-size:12px;"
        )
        header.addWidget(self.title)
        header.addStretch(1)
        header.addWidget(self.status)
        layout.addLayout(header)

        action_row = QHBoxLayout()
        self.start_btn = QPushButton("Start Demo")
        self.start_btn.setObjectName("PrimaryButton")
        self.stop_btn = QPushButton("End Demo")
        self.stop_btn.setEnabled(False)
        action_row.addWidget(self.start_btn)
        action_row.addWidget(self.stop_btn)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        self.detail_frame = QFrame()
        detail_layout = QVBoxLayout(self.detail_frame)
        detail_layout.setContentsMargins(8, 8, 8, 8)
        detail_layout.setSpacing(6)

        self.step_label = QLabel("Step 1/1")
        self.step_label.setStyleSheet("font-size:12px; color:#9aa0c6;")
        self.step_title = QLabel("-")
        self.step_title.setStyleSheet("font-size:16px; font-weight:600;")
        self.step_description = QLabel("-")
        self.step_description.setWordWrap(True)
        self.step_description.setStyleSheet("font-size:13px; color:#c9ccf5;")
        self.moment_label = QLabel("Cinematic Moment: —")
        self.moment_label.setStyleSheet("font-size:12px; color:#8e93c8;")

        detail_layout.addWidget(self.step_label)
        detail_layout.addWidget(self.step_title)
        detail_layout.addWidget(self.step_description)
        detail_layout.addWidget(self.moment_label)
        layout.addWidget(self.detail_frame)

        nav_row = QHBoxLayout()
        self.prev_btn = QPushButton("Back")
        self.next_btn = QPushButton("Next")
        nav_row.addWidget(self.prev_btn)
        nav_row.addWidget(self.next_btn)
        nav_row.addStretch(1)
        layout.addLayout(nav_row)
        self.nav_row = nav_row

        self.opacity_effect = QGraphicsOpacityEffect(self.detail_frame)
        self.detail_frame.setGraphicsEffect(self.opacity_effect)
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.fade_anim.setDuration(280)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.prev_btn.clicked.connect(self.prev_step)
        self.next_btn.clicked.connect(self.next_step)

        self._refresh_ui()

    def set_steps(self, steps: list[dict[str, str]]) -> None:
        self.steps = steps
        self.current_index = 0
        self._refresh_ui()

    def start(self) -> None:
        if not self.steps:
            return
        self.active = True
        self.current_index = 0
        self._refresh_ui()
        self._animate_step()

    def stop(self) -> None:
        self.active = False
        self._refresh_ui()

    def next_step(self) -> None:
        if not self.active:
            self.start()
            return
        if self.current_index < len(self.steps) - 1:
            self.current_index += 1
            self._refresh_ui()
            self._animate_step()

    def prev_step(self) -> None:
        if not self.active:
            return
        if self.current_index > 0:
            self.current_index -= 1
            self._refresh_ui()
            self._animate_step()

    def _refresh_ui(self) -> None:
        has_steps = bool(self.steps)
        self.start_btn.setEnabled(not self.active and has_steps)
        self.stop_btn.setEnabled(self.active)
        self.detail_frame.setVisible(self.active)
        self.prev_btn.setEnabled(self.active and self.current_index > 0)
        self.next_btn.setEnabled(self.active and self.current_index < len(self.steps) - 1)

        status_text = "Active" if self.active else "Idle"
        status_color = "#2b2f52" if self.active else "#1c2036"
        self.status.setText(status_text)
        self.status.setStyleSheet(
            f"background:{status_color}; border-radius:12px; padding:0 10px; font-size:12px;"
        )

        if not has_steps:
            self.step_label.setText("Step --")
            self.step_title.setText("No demo steps available")
            self.step_description.setText("Add demo steps to begin the guided tour.")
            self.moment_label.setText("Cinematic Moment: —")
            return

        step = self.steps[self.current_index]
        self.step_label.setText(f"Step {self.current_index + 1}/{len(self.steps)}")
        self.step_title.setText(step.get("title", "-"))
        self.step_description.setText(step.get("description", "-"))
        moment = step.get("moment", "Aurora pulse")
        self.moment_label.setText(f"Cinematic Moment: {moment}")

    def _animate_step(self) -> None:
        self.fade_anim.stop()
        self.opacity_effect.setOpacity(0.0)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()
