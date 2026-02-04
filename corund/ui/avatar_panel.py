from __future__ import annotations

import pathlib

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from corund.ui.juicy_button import JuicyChipButton, JuicyIconButton
from corund.ui.theme import get_theme_manager


class AvatarFaceWidget(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(220, 260)
        self._emotion = "calm"
        self._pulse = 0.0
        self._pixmap = self._load_face()

        self._timer = QTimer(self)
        self._timer.setInterval(60)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _load_face(self) -> QPixmap | None:
        path = pathlib.Path("assets/avatar/face_idle.webp")
        if not path.exists():
            return None
        pm = QPixmap(str(path))
        return None if pm.isNull() else pm

    def set_emotion(self, tag: str) -> None:
        self._emotion = tag
        self.update()

    def _tick(self) -> None:
        if get_theme_manager().reduced_motion:
            self._pulse = 0.0
        else:
            self._pulse = (self._pulse + 0.07) % 6.28
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(10, 10, -10, -10)

        tokens = get_theme_manager().tokens.colors
        ring = QColor(tokens.get(f"ring.{self._emotion}", tokens["ring.calm"]))
        ring.setAlpha(140)
        glow = QColor(ring)
        glow.setAlpha(60)

        painter.setBrush(QColor(16, 18, 30))
        painter.setPen(QColor(38, 42, 72))
        painter.drawRoundedRect(rect, 24, 24)

        painter.setBrush(glow)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect.center(), rect.width() * 0.4, rect.width() * 0.4)

        if self._pixmap:
            pm = self._pixmap.scaled(rect.size().toSize(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.setClipRect(rect)
            painter.drawPixmap(rect.topLeft(), pm)
        else:
            painter.setPen(QColor(82, 89, 134))
            painter.drawText(rect, Qt.AlignCenter, "Avatar\nPlaceholder")

        painter.setPen(QColor(255, 255, 255, 60))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect, 24, 24)


class AvatarPanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("panel", True)
        self.emotion_tag = "calm"
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Etherea Presence")
        title.setObjectName("TitleText")
        header.addWidget(title)
        header.addStretch(1)
        self.kill_switch = JuicyIconButton("⛔")
        header.addWidget(self.kill_switch)
        layout.addLayout(header)

        self.face = AvatarFaceWidget()
        layout.addWidget(self.face, alignment=Qt.AlignCenter)

        self.dialogue = QLabel("“Ready when you are. Start a calm focus?”")
        self.dialogue.setWordWrap(True)
        self.dialogue.setStyleSheet("color:#cdd1f6;")
        layout.addWidget(self.dialogue)

        chips = QHBoxLayout()
        chips.addWidget(JuicyChipButton("Focus ON"))
        chips.addWidget(JuicyChipButton("Calm Reset Ready"))
        layout.addLayout(chips)

        toggles = QHBoxLayout()
        toggles.addWidget(JuicyIconButton("🔊"))
        toggles.addWidget(JuicyIconButton("🎙️"))
        toggles.addStretch(1)
        layout.addLayout(toggles)

    def update_ei(self, vec: dict) -> None:
        focus = vec.get("focus", 0.5)
        stress = vec.get("stress", 0.2)
        if stress > 0.6:
            self.emotion_tag = "stress"
        elif focus > 0.7:
            self.emotion_tag = "focus"
        else:
            self.emotion_tag = "calm"
        self.face.set_emotion(self.emotion_tag)
