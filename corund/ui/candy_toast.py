from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget


class CandyToast(QFrame):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CandyToast")
        self.setStyleSheet(
            """
            QFrame#CandyToast {
                background: rgba(255, 255, 255, 230);
                border-radius: 14px;
                border: 1px solid rgba(255, 255, 255, 150);
            }
            QLabel { color: #4a1463; font-weight: 600; }
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.addWidget(QLabel(text))

        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(0.0)

        self._fade = QPropertyAnimation(self._opacity, b"opacity")
        self._fade.setDuration(900)
        self._fade.setStartValue(0.0)
        self._fade.setKeyValueAt(0.2, 1.0)
        self._fade.setEndValue(0.0)
        self._fade.setEasingCurve(QEasingCurve.OutQuad)

        self._slide = QPropertyAnimation(self, b"pos")
        self._slide.setDuration(900)
        self._slide.setEasingCurve(QEasingCurve.OutBounce)

    def play(self, start: QPoint, end: QPoint) -> None:
        self.move(start)
        self.show()
        self._slide.setStartValue(start)
        self._slide.setEndValue(end)
        self._fade.start()
        self._slide.start()
        QTimer.singleShot(1400, self.close)


class CandyToastManager:
    def __init__(self, parent: QWidget) -> None:
        self.parent = parent

    def show_toast(self, text: str) -> None:
        toast = CandyToast(text, self.parent)
        start = self.parent.mapToGlobal(self.parent.rect().topRight())
        end = start + QPoint(-toast.sizeHint().width() - 20, 30)
        toast.play(start, end)
