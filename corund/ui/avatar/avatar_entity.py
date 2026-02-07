from __future__ import annotations

import math
import random
import time
from typing import Optional

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QFont, QFontMetrics, QPainter, QColor
from PySide6.QtWidgets import QGraphicsObject

from corund.ui.avatar.avatar_renderer import AvatarRenderer


class SpeechBubbleItem(QGraphicsObject):
    def __init__(self, text: str = "", parent: Optional[QGraphicsObject] = None) -> None:
        super().__init__(parent)
        self._text = text
        self._font = QFont("Segoe UI", 9)
        self._padding = 8
        self.setVisible(False)

    def set_text(self, text: str) -> None:
        self._text = text
        self.setVisible(bool(text))
        self.prepareGeometryChange()
        self.update()

    def boundingRect(self) -> QRectF:  # noqa: N802
        metrics = QFontMetrics(self._font)
        text_rect = metrics.boundingRect(0, 0, 220, 80, 0, self._text)
        width = text_rect.width() + self._padding * 2
        height = text_rect.height() + self._padding * 2
        return QRectF(0, 0, width, height)

    def paint(self, painter: QPainter, option, widget=None) -> None:  # noqa: ANN001
        if not self._text:
            return
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.boundingRect()
        painter.setBrush(QColor(255, 255, 255, 230))
        painter.setPen(QColor(255, 255, 255, 120))
        painter.drawRoundedRect(rect, 10, 10)
        painter.setFont(self._font)
        painter.setPen(QColor(60, 30, 90))
        painter.drawText(rect.adjusted(self._padding, self._padding, -self._padding, -self._padding), 0, self._text)
        painter.restore()


class AvatarEntity(QGraphicsObject):
    def __init__(self, radius: float = 36.0, parent: Optional[QGraphicsObject] = None) -> None:
        super().__init__(parent)
        self.radius = radius
        self.velocity = QPointF(0.0, 0.0)
        self.acceleration = QPointF(0.0, 0.0)
        self.max_speed = 120.0
        self.max_force = 220.0
        self._pulse = 0.0
        self._blink_phase = random.random() * math.tau
        self._mouth_open = 0.1
        self._renderer = AvatarRenderer()
        self._target: Optional[QPointF] = None
        self._freeze = False
        self._reduce_motion = False
        self._free_roam = True
        self._dragging = False
        self.mood = "calm"

        self.bubble = SpeechBubbleItem(parent=self)
        self.bubble.setPos(-self.radius, -self.radius * 2.2)

    def boundingRect(self) -> QRectF:  # noqa: N802
        size = self.radius * 2
        return QRectF(-self.radius, -self.radius, size, size)

    def set_target(self, target: Optional[QPointF]) -> None:
        self._target = target

    def set_dragging(self, dragging: bool) -> None:
        self._dragging = dragging

    def set_mouth_open(self, value: float) -> None:
        self._mouth_open = max(0.0, min(1.0, value))

    def set_freeze(self, freeze: bool) -> None:
        self._freeze = freeze

    def set_reduce_motion(self, reduce_motion: bool) -> None:
        self._reduce_motion = reduce_motion

    def set_free_roam(self, free_roam: bool) -> None:
        self._free_roam = free_roam

    def set_bubble_text(self, text: str) -> None:
        self.bubble.set_text(text)

    def paint(self, painter: QPainter, option, widget=None) -> None:  # noqa: ANN001
        rect = self.boundingRect()
        blink = abs(math.sin(self._blink_phase))
        self._renderer.paint(painter, rect, self._pulse, self.mood, blink, self._mouth_open)

    def tick(self, dt: float, bounds: QRectF, wander_target: Optional[QPointF]) -> None:
        if self._freeze or self._dragging:
            return

        if not self._reduce_motion:
            self._pulse += dt * 3.2
            self._blink_phase += dt * 6.0

        target = self._target or (wander_target if self._free_roam else None)
        steering = QPointF(0.0, 0.0)
        if target is not None:
            desired = QPointF(target.x() - self.x(), target.y() - self.y())
            distance = math.hypot(desired.x(), desired.y())
            if distance > 0.0:
                desired = _scale(desired, 1.0 / distance)
                desired = _scale(desired, min(self.max_speed, distance * 2.0))
                steering = _sub(desired, self.velocity)

        wander = QPointF(0.0, 0.0)
        if self._free_roam and target is None:
            angle = random.uniform(0, math.tau)
            wander = _scale(QPointF(math.cos(angle), math.sin(angle)), 20.0)

        steering = _add(steering, wander)
        magnitude = math.hypot(steering.x(), steering.y())
        if magnitude > self.max_force:
            steering = _scale(steering, self.max_force / magnitude)

        self.acceleration = steering
        self.velocity = _add(self.velocity, _scale(self.acceleration, dt))

        speed = math.hypot(self.velocity.x(), self.velocity.y())
        if speed > self.max_speed:
            self.velocity = _scale(self.velocity, self.max_speed / speed)

        new_pos = _add(QPointF(self.x(), self.y()), _scale(self.velocity, dt))
        new_pos.setX(max(bounds.left() + self.radius, min(bounds.right() - self.radius, new_pos.x())))
        new_pos.setY(max(bounds.top() + self.radius, min(bounds.bottom() - self.radius, new_pos.y())))
        self.setPos(new_pos)
        self.update()

    def jump_to_bounds_center(self, bounds: QRectF) -> None:
        center = bounds.center()
        self.setPos(center)
        self.velocity = QPointF(0.0, 0.0)
        self.acceleration = QPointF(0.0, 0.0)


def _scale(point: QPointF, factor: float) -> QPointF:
    return QPointF(point.x() * factor, point.y() * factor)


def _add(a: QPointF, b: QPointF) -> QPointF:
    return QPointF(a.x() + b.x(), a.y() + b.y())


def _sub(a: QPointF, b: QPointF) -> QPointF:
    return QPointF(a.x() - b.x(), a.y() - b.y())
