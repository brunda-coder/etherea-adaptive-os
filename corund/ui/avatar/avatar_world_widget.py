from __future__ import annotations

import time

from PySide6.QtCore import QElapsedTimer, QPointF, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from corund.ui.avatar.avatar_brain import AvatarBrain
from corund.ui.avatar.avatar_entity import AvatarEntity
from corund.ui.avatar.surprises import create_sparkle_burst
from corund.ui.theme import get_theme_manager


class AvatarWorldWidget(QGraphicsView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("background: transparent; border: none;")
        self.setMouseTracking(True)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.brain = AvatarBrain()
        self.entity = AvatarEntity(radius=36.0)
        self.scene.addItem(self.entity)

        self._free_roam = True
        self._freeze = False
        self._reduce_motion = False
        self._enabled = True

        self._elapsed = QElapsedTimer()
        self._elapsed.start()

        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(16)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start()

        self._last_idle_check = time.time()
        self._last_surprise = 0.0

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._sync_bounds()

    def _sync_bounds(self) -> None:
        rect = self.viewport().rect()
        self.setSceneRect(0, 0, rect.width(), rect.height())
        self.entity.jump_to_bounds_center(self.scene.sceneRect())

    def set_free_roam(self, enabled: bool) -> None:
        self._free_roam = enabled
        self.entity.set_free_roam(enabled)

    def set_freeze(self, enabled: bool) -> None:
        self._freeze = enabled
        self.entity.set_freeze(enabled)

    def set_reduce_motion(self, enabled: bool) -> None:
        self._reduce_motion = enabled
        self.entity.set_reduce_motion(enabled)
        self._tick_timer.setInterval(33 if enabled else 16)

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self.setVisible(enabled)

    def set_dramatic_mode(self, enabled: bool) -> None:
        self.brain.dramatic_mode = enabled

    def set_anchor_target(self, point: QPointF) -> None:
        self.entity.set_target(point)

    def clear_anchor_target(self) -> None:
        self.entity.set_target(None)

    def go_to_anchor(self, name: str) -> None:
        bounds = self.scene.sceneRect()
        anchors = {
            "aurora_ring": QPointF(bounds.width() * 0.25, bounds.height() * 0.3),
            "command_palette": QPointF(bounds.width() * 0.75, bounds.height() * 0.75),
        }
        target = anchors.get(name)
        if target is not None:
            self.set_anchor_target(target)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if not self._enabled:
            return
        line = self.brain.on_click()
        self._show_bubble(line)
        self._trigger_surprise()
        super().mousePressEvent(event)

    def enterEvent(self, event) -> None:  # noqa: N802
        if not self._enabled:
            return
        line = self.brain.on_hover()
        self._show_bubble(line)
        super().enterEvent(event)

    def _show_bubble(self, text: str) -> None:
        self.entity.set_bubble_text(text)

    def _trigger_surprise(self) -> None:
        now = time.time()
        if now - self._last_surprise < 4.0:
            return
        color = QColor(get_theme_manager().tokens.colors["accent.secondary"])
        create_sparkle_burst(self.scene, self.entity.pos(), color)
        self._last_surprise = now

    def _tick(self) -> None:
        if not self._enabled:
            return

        dt = min(0.05, self._elapsed.restart() / 1000.0)
        bounds = self.scene.sceneRect()
        now = time.time()
        wander_target = self.brain.update(bounds, now)

        theme_reduced = get_theme_manager().reduced_motion
        self.entity.set_free_roam(self._free_roam)
        self.entity.set_reduce_motion(self._reduce_motion or theme_reduced)
        self._tick_timer.setInterval(33 if (self._reduce_motion or theme_reduced) else 16)
        self.entity.tick(dt, bounds, wander_target)

        if now - self._last_idle_check > 6.0:
            line = self.brain.on_idle()
            self._show_bubble(line)
            self._last_idle_check = now
