from __future__ import annotations

import math

from PySide6.QtCore import QEasingCurve, Property, QPropertyAnimation, QRectF, QSize, QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QPushButton

from corund.ui.theme import get_theme_manager


class JuicyButton(QPushButton):
    def __init__(
        self,
        text: str = "",
        variant: str = "primary",
        *,
        icon_only: bool = False,
        parent=None,
    ) -> None:
        super().__init__(text, parent)
        self.variant = variant
        self.icon_only = icon_only
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(False)
        self._scale = 1.0
        self._press_depth = 0.0
        self._hovered = False
        self._loading = False
        self._spin = 0.0

        self._scale_anim = QPropertyAnimation(self, b"scale", self)
        self._scale_anim.setDuration(160)
        self._scale_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._press_anim = QPropertyAnimation(self, b"pressDepth", self)
        self._press_anim.setDuration(120)
        self._press_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._loading_timer = QTimer(self)
        self._loading_timer.setInterval(50)
        self._loading_timer.timeout.connect(self._tick_spinner)

        self.setMinimumHeight(38)

    def sizeHint(self):
        hint = super().sizeHint()
        return hint.expandedTo(QSize(120, 38))

    def set_loading(self, loading: bool) -> None:
        self._loading = loading
        if loading:
            self._loading_timer.start()
        else:
            self._loading_timer.stop()
        self.update()

    def _tick_spinner(self) -> None:
        self._spin = (self._spin + 0.12) % (2 * math.pi)
        self.update()

    def enterEvent(self, event):
        self._hovered = True
        self._animate_scale(1.02)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._animate_scale(1.0)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._animate_press(1.0)
            self._animate_scale(0.96)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._animate_press(0.0)
            self._animate_scale(1.0, spring=True)
        super().mouseReleaseEvent(event)

    def _animate_scale(self, target: float, spring: bool = False) -> None:
        self._scale_anim.stop()
        self._scale_anim.setDuration(200 if spring else 160)
        self._scale_anim.setEasingCurve(QEasingCurve.OutBack if spring else QEasingCurve.OutCubic)
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(target)
        self._scale_anim.start()

    def _animate_press(self, target: float) -> None:
        self._press_anim.stop()
        self._press_anim.setStartValue(self._press_depth)
        self._press_anim.setEndValue(target)
        self._press_anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        tokens = get_theme_manager().tokens
        colors = tokens.colors
        radius = tokens.radii["button"]
        base = QColor(colors["accent.primary"])
        secondary = QColor(colors["bg.overlay"])
        danger = QColor(colors["state.danger"])
        ghost = QColor(0, 0, 0, 0)

        if self.variant == "secondary":
            fill = secondary
        elif self.variant == "danger":
            fill = danger
        elif self.variant == "ghost":
            fill = ghost
        elif self.variant == "chip":
            fill = QColor(colors["bg.overlay"])
        else:
            fill = base

        if not self.isEnabled():
            fill.setAlpha(120)

        shadow_strength = 18 * (1.0 - self._press_depth)
        highlight = QColor(255, 255, 255, 40 if self._hovered else 20)

        scaled = rect.adjusted(4, 4, -4, -4)
        center = scaled.center()
        w = scaled.width() * self._scale
        h = scaled.height() * self._scale
        scaled_rect = QRectF(center.x() - w / 2, center.y() - h / 2 + self._press_depth * 2, w, h)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, int(shadow_strength)))
        shadow_rect = scaled_rect.adjusted(0, 6, 0, 6)
        painter.drawRoundedRect(shadow_rect, radius + 2, radius + 2)

        painter.setBrush(fill)
        painter.drawRoundedRect(scaled_rect, radius, radius)

        painter.setBrush(highlight)
        highlight_rect = scaled_rect.adjusted(3, 3, -3, -scaled_rect.height() * 0.55)
        painter.drawRoundedRect(highlight_rect, radius - 4, radius - 4)

        painter.setPen(QPen(QColor(255, 255, 255, 45), 1))
        painter.drawRoundedRect(scaled_rect, radius, radius)

        painter.setPen(QColor(colors["text.primary"]))
        if self.variant == "ghost":
            painter.setPen(QColor(colors["text.secondary"]))

        if self._loading:
            self._draw_spinner(painter, scaled_rect)
        else:
            painter.drawText(scaled_rect, Qt.AlignCenter, self.text())

    def _draw_spinner(self, painter: QPainter, rect: Qt.QRectF) -> None:
        size = min(rect.width(), rect.height()) * 0.35
        center = rect.center()
        painter.setPen(QPen(QColor(255, 255, 255, 180), 2))
        start_angle = int(math.degrees(self._spin) * 16)
        span = int(120 * 16)
        painter.drawArc(
            QRectF(center.x() - size / 2, center.y() - size / 2, size, size),
            start_angle,
            span,
        )

    def getScale(self) -> float:
        return self._scale

    def setScale(self, value: float) -> None:
        self._scale = value
        self.update()

    def getPressDepth(self) -> float:
        return self._press_depth

    def setPressDepth(self, value: float) -> None:
        self._press_depth = value
        self.update()

    scale = Property(float, getScale, setScale)
    pressDepth = Property(float, getPressDepth, setPressDepth)


class JuicyIconButton(JuicyButton):
    def __init__(self, text: str = "", variant: str = "ghost", parent=None) -> None:
        super().__init__(text, variant=variant, icon_only=True, parent=parent)
        self.setFixedSize(40, 40)


class JuicyChipButton(JuicyButton):
    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, variant="chip", parent=parent)
        self.setCheckable(True)
        self.setMinimumHeight(30)
