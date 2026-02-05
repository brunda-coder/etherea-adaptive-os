from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPointF, QPropertyAnimation, QRectF
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QGraphicsObject, QGraphicsScene


class SparkleBurst(QGraphicsObject):
    def __init__(self, color: QColor, radius: float = 24.0) -> None:
        super().__init__()
        self._color = color
        self._radius = radius
        self.setOpacity(0.0)
        self.setScale(0.2)

        self._fade = QPropertyAnimation(self, b"opacity")
        self._fade.setDuration(850)
        self._fade.setStartValue(0.0)
        self._fade.setKeyValueAt(0.5, 1.0)
        self._fade.setEndValue(0.0)
        self._fade.setEasingCurve(QEasingCurve.OutQuad)

        self._scale = QPropertyAnimation(self, b"scale")
        self._scale.setDuration(850)
        self._scale.setStartValue(0.2)
        self._scale.setEndValue(1.2)
        self._scale.setEasingCurve(QEasingCurve.OutBack)

        self._fade.finished.connect(self._cleanup)

    def boundingRect(self) -> QRectF:  # noqa: N802
        size = self._radius * 2
        return QRectF(-self._radius, -self._radius, size, size)

    def paint(self, painter: QPainter, option, widget=None) -> None:  # noqa: ANN001
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self._color)
        painter.setPen(self._color)
        painter.drawEllipse(self.boundingRect())

    def play(self) -> None:
        self._fade.start()
        self._scale.start()

    def _cleanup(self) -> None:
        scene = self.scene()
        if scene:
            scene.removeItem(self)
        self.deleteLater()


def create_sparkle_burst(scene: QGraphicsScene, position: QPointF, color: QColor) -> SparkleBurst:
    burst = SparkleBurst(color)
    burst.setPos(position)
    scene.addItem(burst)
    burst.play()
    return burst
