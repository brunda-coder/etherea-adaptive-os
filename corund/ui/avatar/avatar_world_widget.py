from __future__ import annotations

import time

from PySide6.QtCore import QElapsedTimer, QPointF, QTimer, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from corund.avatar_assets import AvatarAssetManifestLoader
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

        self.manifest = AvatarAssetManifestLoader().load()
        self.movement_mode = "wander"

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

        # Ensure scene bounds are initialized (prevents blank avatar on first show)
        QTimer.singleShot(0, self._ensure_bounds_ready)

        self._last_idle_check = time.time()
        self._last_surprise = 0.0

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._ensure_bounds_ready()

    def _ensure_bounds_ready(self) -> None:
        """Initialize scene rect when the viewport becomes available."""
        try:
            rect = self.viewport().rect()
            if rect.width() <= 2 or rect.height() <= 2:
                # Viewport not laid out yet; try again shortly.
                QTimer.singleShot(50, self._ensure_bounds_ready)
                return
            self._sync_bounds()
        except Exception:
            QTimer.singleShot(50, self._ensure_bounds_ready)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._sync_bounds()

    def _sync_bounds(self) -> None:
        rect = self.viewport().rect()
        self.setSceneRect(0, 0, rect.width(), rect.height())
        self.entity.jump_to_bounds_center(self.scene.sceneRect())

    def diagnostics(self) -> dict:
        return {
            "assets_count": self.manifest.total_count,
            "movement_mode": self.movement_mode,
            "mood": self.entity.mood,
        }

    def set_movement_mode(self, mode: str) -> None:
        self.movement_mode = mode
        if mode == "follow":
            self._free_roam = False
        elif mode == "locked":
            self._free_roam = False
            self.entity.set_target(self.scene.sceneRect().center())
        else:
            self._free_roam = True

    def set_free_roam(self, enabled: bool) -> None:
        self._free_roam = bool(enabled)

    def set_reduce_motion(self, enabled: bool) -> None:
        self._reduce_motion = bool(enabled)

    def set_freeze(self, enabled: bool) -> None:
        self._freeze = bool(enabled)
        if self._freeze:
            self.entity.freeze()
        else:
            self.entity.unfreeze()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        self.entity.setVisible(self._enabled)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if not self._enabled:
            return
        if event.button() == Qt.LeftButton:
            self.entity.set_dragging(True)
            line = self.brain.on_click()
            self._show_bubble(line)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if not self._enabled:
            return
        if self.entity.dragging:
            pos = self.mapToScene(event.pos())
            self.entity.setPos(pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if not self._enabled:
            return
        if event.button() == Qt.LeftButton:
            self.entity.set_dragging(False)
        super().mouseReleaseEvent(event)

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
