from __future__ import annotations

import math
import time

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from corund.ui.theme import get_theme_manager


class AuroraRingWidget(QWidget):
    def __init__(self, mode: str = "expanded", parent=None) -> None:
        super().__init__(parent)
        self.mode = mode
        self._t0 = time.time()
        self._pulse = 0.0
        self._state = "calm"

        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self._tick)
        self.timer.start()

    def set_state(self, state: str) -> None:
        self._state = state
        self.update()

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.update()

    def _tick(self) -> None:
        if get_theme_manager().reduced_motion:
            self._pulse = 0.0
        else:
            self._pulse = (time.time() - self._t0) * 1.5
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        tokens = get_theme_manager().tokens.colors
        ring_map = {
            "calm": tokens["ring.calm"],
            "focus": tokens["ring.focus"],
            "stress": tokens["ring.stress"],
            "idle": tokens["ring.idle"],
        }
        color = QColor(ring_map.get(self._state, tokens["ring.idle"]))
        glow = QColor(color)
        glow.setAlpha(60)

        rect = self.rect().adjusted(6, 6, -6, -6)
        base_width = 4 if self.mode == "mini" else 6
        pulse = 1.0 + 0.08 * math.sin(self._pulse)

        painter.setPen(Qt.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(rect.adjusted(-4, -4, 4, 4))

        painter.setBrush(Qt.NoBrush)
        pen = QPen(color, base_width * pulse)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawEllipse(rect)

        if get_theme_manager().theme_name == "candy":
            sparkle = QPen(QColor(tokens["accent.secondary"]), 2)
            painter.setPen(sparkle)
            for offset in range(0, 360, 45):
                angle = math.radians(offset + self._pulse * 20)
                x = rect.center().x() + math.cos(angle) * rect.width() * 0.46
                y = rect.center().y() + math.sin(angle) * rect.height() * 0.46
                painter.drawPoint(int(x), int(y))
