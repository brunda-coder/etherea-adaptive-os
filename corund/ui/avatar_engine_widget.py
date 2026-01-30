from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import List, Tuple

from PySide6.QtCore import QTimer, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QRadialGradient, QLinearGradient, QPen
from PySide6.QtWidgets import QWidget

from corund.ui.avatar_engine.engine import AvatarEngine
from corund.ui.avatar_engine.registry import AVATARS, AvatarSpec


def _qcolor(rgb: Tuple[int, int, int], a: int = 255) -> QColor:
    r, g, b = rgb
    return QColor(int(r), int(g), int(b), int(a))


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    size: float


class AvatarEngineWidget(QWidget):
    """
    Cinematic 2D avatar scene (fast, stable, Termux-friendly).
    - Dynamic gradient background + drift
    - Particle field
    - Aura ring + core glow pulse
    - Multi-avatar switch (Aurora/Ethera/Sentinel)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.engine = AvatarEngine()

        self._t_last = time.time()
        self._t = 0.0

        self._particles: List[Particle] = []
        self._particle_acc = 0.0

        self._bg_phase = 0.0

        self.setMinimumSize(420, 420)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_frame)
        self._timer.start(33)  # ~30fps

    # ---- Public API (called by UI / signals) ----
    def set_avatar(self, key: str):
        self.engine.set_avatar(key)

    def update_ei(self, vec: dict):
        self.engine.update_ei(vec)

    # ---- Animation loop ----
    def _on_frame(self):
        now = time.time()
        dt = max(0.001, min(0.050, now - self._t_last))
        self._t_last = now
        self._t += dt

        # engine tick (handles switching)
        self.engine.tick(dt)

        # background drift
        drift = self.engine.avatar.drift_speed * self.engine.motion_multiplier
        self._bg_phase += dt * drift

        # particles
        self._spawn_particles(dt)
        self._update_particles(dt)

        self.update()

    def _spawn_particles(self, dt: float):
        spec = self.engine.avatar
        rate = spec.particle_rate * self.engine.motion_multiplier
        self._particle_acc += dt * rate

        # less particles when stress is high (calmer)
        stress = self.engine.ei.get("stress", 0.2)
        damp = 1.0 - 0.6 * stress
        self._particle_acc *= max(0.25, damp)

        while self._particle_acc >= 1.0:
            self._particle_acc -= 1.0
            w = max(1, self.width())
            h = max(1, self.height())

            # spawn near edges
            edge = random.randint(0, 3)
            if edge == 0:
                x, y = -10.0, random.uniform(0, h)
            elif edge == 1:
                x, y = w + 10.0, random.uniform(0, h)
            elif edge == 2:
                x, y = random.uniform(0, w), -10.0
            else:
                x, y = random.uniform(0, w), h + 10.0

            angle = random.uniform(0, math.tau)
            speed = random.uniform(20.0, 80.0) * (0.6 + 0.8 * self.engine.motion_multiplier)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            life = random.uniform(1.6, 3.2)
            size = random.uniform(1.0, 2.5)

            self._particles.append(Particle(x=x, y=y, vx=vx, vy=vy, life=life, size=size))

        # cap
        if len(self._particles) > 180:
            self._particles = self._particles[-180:]

    def _update_particles(self, dt: float):
        alive = []
        for p in self._particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.life -= dt
            if p.life > 0:
                alive.append(p)
        self._particles = alive

    # ---- Painting ----
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = self.rect()

        spec = self.engine.avatar
        focus = self.engine.ei.get("focus", 0.5)
        stress = self.engine.ei.get("stress", 0.2)
        energy = self.engine.ei.get("energy", 0.6)

        # Background gradient with slow drift
        shift = 0.5 + 0.15 * math.sin(self._bg_phase * 1.2)
        grad = QLinearGradient(0, 0, rect.width(), rect.height())
        grad.setColorAt(0.0, _qcolor(spec.bg_a, 255))
        grad.setColorAt(shift, _qcolor(spec.bg_b, 255))
        grad.setColorAt(1.0, _qcolor(spec.bg_a, 255))
        painter.fillRect(rect, grad)

        # Subtle vignette
        vign = QRadialGradient(rect.center(), rect.width() * 0.75)
        vign.setColorAt(0.0, QColor(0, 0, 0, 0))
        vign.setColorAt(1.0, QColor(0, 0, 0, 140))
        painter.fillRect(rect, vign)

        # Particles
        particle_color = _qcolor(spec.particle, 160)
        for p in self._particles:
            alpha = int(180 * max(0.0, min(1.0, p.life / 2.2)))
            c = QColor(particle_color)
            c.setAlpha(alpha)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(c)
            painter.drawEllipse(QRectF(p.x, p.y, p.size, p.size))

        # Avatar ring + core glow
        cx = rect.center().x()
        cy = rect.center().y()

        base_r = min(rect.width(), rect.height()) * 0.26
        breathing = 1.0 + 0.04 * math.sin(self._t * (1.1 + energy))
        ring_r = base_r * breathing

        # Glow pulse (reduced if stress is high)
        pulse_speed = spec.pulse_speed * (0.8 + 0.8 * self.engine.motion_multiplier)
        pulse = 0.55 + 0.45 * math.sin(self._t * pulse_speed * math.tau)
        glow = self.engine.glow_intensity * (0.85 - 0.4 * stress) + 0.15 * pulse
        glow = max(0.15, min(1.0, glow))

        # Outer aura glow
        aura = QRadialGradient(cx, cy, ring_r * 2.2)
        aura.setColorAt(0.0, QColor(0, 0, 0, 0))
        aura.setColorAt(0.55, _qcolor(spec.ring, int(90 * glow)))
        aura.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(rect, aura)

        # Ring stroke
        ring_pen = QPen(_qcolor(spec.ring, int(210 * (0.55 + 0.45 * focus))))
        ring_pen.setWidthF(max(2.0, ring_r * 0.06))
        painter.setPen(ring_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2))

        # Inner core glow
        core_r = ring_r * (0.50 + 0.08 * math.sin(self._t * 2.0))
        core = QRadialGradient(cx, cy, core_r * 1.8)
        core.setColorAt(0.0, _qcolor(spec.core, int(220 * glow)))
        core.setColorAt(0.4, _qcolor(spec.core, int(120 * glow)))
        core.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(core)
        painter.drawEllipse(QRectF(cx - core_r, cy - core_r, core_r * 2, core_r * 2))

        painter.end()
