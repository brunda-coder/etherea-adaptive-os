from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPixmap

from corund.ui.theme import get_theme_manager


class AvatarRenderer:
    def __init__(self) -> None:
        root = Path(__file__).resolve().parents[3]
        self._pixmap = QPixmap(str(root / "assets/avatar/face_idle.webp"))
        if self._pixmap.isNull():
            self._pixmap = QPixmap(str(root / "corund/assets/avatar_hero/base.png"))

    def paint(self, painter: QPainter, rect: QRectF, pulse: float, mood: str, blink: float, mouth_open: float = 0.1) -> None:
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        tokens = get_theme_manager().tokens.colors
        base = QColor(tokens.get("accent.primary", "#ff7adf"))
        glow = QColor(tokens.get("accent.secondary", "#7ee8ff"))
        ring = QColor(tokens.get(f"ring.{mood}", tokens.get("ring.calm", "#a4f4c2")))

        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0.0, glow)
        gradient.setColorAt(1.0, base)

        painter.setBrush(gradient)
        painter.setPen(ring)
        painter.drawEllipse(rect)

        face_rect = rect.adjusted(rect.width() * 0.12, rect.height() * 0.12, -rect.width() * 0.12, -rect.height() * 0.12)
        if not self._pixmap.isNull():
            painter.drawPixmap(face_rect.toRect(), self._pixmap)
        else:
            painter.setBrush(QColor(255, 255, 255, 220))
            painter.setPen(QColor(255, 255, 255, 140))
            painter.drawRoundedRect(face_rect, 14, 14)

        eye_y = face_rect.center().y() - face_rect.height() * 0.1
        blink_height = max(1.0, 8.0 * (1.0 - blink))
        eye_offset = face_rect.width() * 0.18

        painter.setBrush(QColor(60, 30, 90, 200))
        painter.setPen(QColor(60, 30, 90, 240))
        painter.drawRoundedRect(QRectF(face_rect.center().x() - eye_offset - 6, eye_y, 12, blink_height), 4, 4)
        painter.drawRoundedRect(QRectF(face_rect.center().x() + eye_offset - 6, eye_y, 12, blink_height), 4, 4)

        smile_path = QPainterPath()
        mouth_base = face_rect.center().y() + face_rect.height() * 0.20
        mouth_height = 4.0 + 16.0 * max(0.0, min(1.0, mouth_open))
        smile_y = mouth_base + math.sin(pulse) * 1.5
        smile_path.moveTo(face_rect.center().x() - 12, smile_y)
        smile_path.quadTo(face_rect.center().x(), smile_y + mouth_height, face_rect.center().x() + 12, smile_y)
        painter.setPen(QColor(90, 40, 120, 220))
        painter.drawPath(smile_path)

        painter.restore()
