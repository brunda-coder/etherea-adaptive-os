from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from PySide6.QtCore import Qt, QTimer, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

# Optional voice engine hookup (for mouth/viseme)
try:
    from corund.voice_engine import get_voice_engine  # type: ignore
except Exception:
    get_voice_engine = None


def _clamp(x: float, lo: float, hi: float) -> float:
    try:
        return max(lo, min(hi, float(x)))
    except Exception:
        return lo


@dataclass
class _Anim:
    """Small helper to ease values smoothly."""
    v: float
    target: float

    def step(self, dt: float, speed: float) -> float:
        # critically damped-ish lerp
        a = 1.0 - math.exp(-max(0.0, speed) * max(0.0, dt))
        self.v = self.v + (self.target - self.v) * a
        return self.v


class AvatarHeroineWidget(QWidget):
    """
    Lightweight, dependency-safe avatar widget.

    Goals:
      - Always render (no missing imports / no hidden crashes)
      - Subtle "alive" motion (breath, micro-tilt, blink)
      - Mouth motion via VoiceEngine viseme updates (if available)
      - Works on Windows + PyInstaller (pure Qt painting)

    Notes:
      - Not full-body 3D (that phase is deferred), but includes stylized
        shoulders + hands so it *feels* like she can gesture.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(260)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # EI state
        self.ei: Dict[str, float] = {"focus": 0.55, "stress": 0.20, "energy": 0.70, "curiosity": 0.55}
        self.mode: str = "study"
        self.emotion_tag: str = "calm"
        self.thinking: bool = False

        # Theme / accents
        self._theme: str = "dark"
        self._accent_a: Tuple[int, int, int] = (160, 120, 255)
        self._accent_b: Tuple[int, int, int] = (255, 210, 120)

        # Animation clock
        self._t0 = time.time()
        self._last_ts = self._t0

        # Expression channels
        self._mouth = _Anim(0.15, 0.15)     # 0..1
        self._smile = _Anim(0.35, 0.35)     # 0..1

        # Alive motion
        self._tilt = _Anim(0.0, 0.0)        # -1..1
        self._nod = _Anim(0.0, 0.0)         # 0..1 impulse
        self._arm = _Anim(0.0, 0.0)         # 0..1 lift

        # Blink timing
        self._blink = 0.0
        self._blink_t = 0.0
        self._blink_next = 2.2 + random.random() * 2.2

        # Pulse ring
        self._pulse_amp = 0.0
        self._pulse_until = 0.0

        # Optional voice hook
        self._speaking = False
        self._hook_voice()

        # Render loop
        self._timer = QTimer(self)
        self._timer.setInterval(16)  # ~60 fps
        self._timer.timeout.connect(self.update)
        self._timer.start()

    # -------------------------
    # Public API (used by windows)
    # -------------------------
    def set_theme_mode(self, theme: str) -> None:
        theme = (theme or "dark").strip().lower()
        self._theme = "light" if theme.startswith("l") else "dark"
        self.update()

    def set_accent_colors(self, a: Tuple[int, int, int], b: Tuple[int, int, int]) -> None:
        self._accent_a = tuple(int(x) for x in a)
        self._accent_b = tuple(int(x) for x in b)
        self.update()

    def set_thinking(self, on: bool) -> None:
        self.thinking = bool(on)
        # subtle acknowledge
        self.acknowledge()

    def set_mode_persona(self, mode: str) -> None:
        self.mode = (mode or "study").strip().lower()
        self._recompute_emotion_tag()

    def update_ei(self, vec: Dict[str, float]) -> None:
        if not isinstance(vec, dict):
            return
        for k in ("focus", "stress", "energy", "curiosity"):
            if k in vec:
                self.ei[k] = _clamp(float(vec.get(k, self.ei.get(k, 0.5))), 0.0, 1.0)
        self._recompute_emotion_tag()

    def pulse(self, *, intensity: float = 1.2, duration: float = 0.25) -> None:
        self._pulse_amp = max(self._pulse_amp, float(intensity))
        self._pulse_until = time.time() + float(duration)

    def nod(self) -> None:
        self._nod.target = 1.0

    def tilt(self, amount: float) -> None:
        self._tilt.target = _clamp(amount, -1.0, 1.0)

    def acknowledge(self) -> None:
        self.nod()
        self.tilt(0.25 if random.random() > 0.5 else -0.25)
        self._arm.target = 0.7  # small "wave-ready" lift

    # -------------------------
    # Voice hook (mouth + speaking state)
    # -------------------------
    def _hook_voice(self) -> None:
        if get_voice_engine is None:
            return
        try:
            ve = get_voice_engine()
            if hasattr(ve, "viseme_updated"):
                ve.viseme_updated.connect(self._on_viseme)  # type: ignore
            if hasattr(ve, "speaking_state"):
                ve.speaking_state.connect(self._on_speaking)  # type: ignore
        except Exception:
            # Safe no-op: avatar must still run
            return

    def _on_viseme(self, v: float) -> None:
        self._mouth.target = _clamp(float(v), 0.0, 1.0)

    def _on_speaking(self, speaking: bool) -> None:
        self._speaking = bool(speaking)
        # speaking -> slightly raise hands
        self._arm.target = 0.9 if self._speaking else 0.0

    # -------------------------
    # Emotion tag computation (simple but stable)
    # -------------------------
    def _recompute_emotion_tag(self) -> None:
        focus = self.ei.get("focus", 0.55)
        stress = self.ei.get("stress", 0.20)
        energy = self.ei.get("energy", 0.70)

        m = (self.mode or "").lower()
        if m in ("exam", "deep_work"):
            stress = _clamp(stress + 0.05, 0.0, 1.0)
            focus = _clamp(focus + 0.05, 0.0, 1.0)

        if stress > 0.62:
            self.emotion_tag = "stressed"
            self._smile.target = 0.15
        elif focus > 0.72 and stress < 0.45:
            self.emotion_tag = "focused"
            self._smile.target = 0.30
        elif energy > 0.72 and stress < 0.40:
            self.emotion_tag = "cheerful"
            self._smile.target = 0.55
        else:
            self.emotion_tag = "calm"
            self._smile.target = 0.40

    # -------------------------
    # Render
    # -------------------------
    def _advance(self, now: float) -> None:
        dt = max(0.0, min(0.05, now - self._last_ts))
        self._last_ts = now

        # Blink scheduling
        self._blink_t += dt
        if self._blink_t >= self._blink_next:
            self._blink = 1.0  # closed
            self._blink_t = 0.0
            self._blink_next = 2.2 + random.random() * 2.8
        else:
            # reopen smoothly
            self._blink = max(0.0, self._blink - dt * 6.0)

        # Ease values
        self._mouth.step(dt, 10.0)
        self._smile.step(dt, 6.0)
        self._tilt.step(dt, 5.0)
        self._arm.step(dt, 7.0)

        # Nod impulse decay
        if self._nod.target > 0.0:
            self._nod.v = 1.0
            self._nod.target = 0.0
        else:
            self._nod.v = max(0.0, self._nod.v - dt * 3.5)

    def paintEvent(self, event) -> None:  # noqa: N802
        now = time.time()
        t = now - self._t0
        self._advance(now)

        w = float(self.width())
        h = float(self.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Background is transparent; we draw a soft glass panel
        if self._theme == "dark":
            panel = QColor(14, 14, 24, 190)
            border = QColor(60, 60, 90, 120)
            text = QColor(235, 235, 255, 220)
            outer_bg = QColor(0, 0, 0, 0)
        else:
            panel = QColor(255, 255, 255, 210)
            border = QColor(40, 40, 60, 80)
            text = QColor(25, 25, 40, 220)
            outer_bg = QColor(0, 0, 0, 0)

        painter.fillRect(self.rect(), outer_bg)

        card = QRectF(10, 10, w - 20, h - 20)
        painter.setBrush(QBrush(panel))
        painter.setPen(QPen(border, 1))
        painter.drawRoundedRect(card, 18, 18)

        # Center + gentle alive offsets
        cx = card.center().x()
        cy = card.center().y() - 6

        breath = 0.8 * math.sin(t * 1.6)
        tilt = self._tilt.v
        nod = self._nod.v

        # Ring
        focus = self.ei.get("focus", 0.55)
        stress = self.ei.get("stress", 0.20)
        energy = self.ei.get("energy", 0.70)

        base = min(card.width(), card.height()) * 0.34
        pulse = 0.0
        if now < self._pulse_until:
            pulse = 0.18 * self._pulse_amp * (0.5 + 0.5 * math.sin(t * 14.0))
        else:
            self._pulse_amp = max(0.0, self._pulse_amp * 0.92)

        ring_r = base * (1.0 + pulse) * (0.98 + 0.02 * math.sin(t * 2.1))

        # Apply head motion by shifting ring center slightly
        center = QPointF(cx + tilt * 6.0, cy + breath * 2.2 + nod * 3.0)

        a = QColor(self._accent_a[0], self._accent_a[1], self._accent_a[2], 190)
        b = QColor(self._accent_b[0], self._accent_b[1], self._accent_b[2], 160)

        ring_pen = QPen(a, 6 + 6 * focus + 4 * pulse)
        ring_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(ring_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, ring_r, ring_r)

        glow_pen = QPen(QColor(b.red(), b.green(), b.blue(), 40), 18 + 14 * energy + 18 * pulse)
        glow_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(glow_pen)
        painter.drawEllipse(center, ring_r, ring_r)

        # Face + shoulders (stylized)
        face_r = ring_r * 0.52
        face_color = QColor(25, 25, 35, 255) if self._theme == "dark" else QColor(235, 236, 245, 255)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(face_color))
        painter.drawEllipse(center, face_r, face_r)

        # Shoulders + torso base
        torso_w = face_r * 1.6
        torso_h = face_r * 1.05
        torso_y = center.y() + face_r * 0.78 + breath * 1.0
        torso = QRectF(center.x() - torso_w / 2, torso_y - torso_h / 2, torso_w, torso_h)
        torso_color = QColor(20, 20, 32, 240) if self._theme == "dark" else QColor(245, 245, 252, 240)
        painter.setBrush(QBrush(torso_color))
        painter.drawRoundedRect(torso, 18, 18)

        # Hands (two soft circles) – "wave" illusion
        arm_lift = self._arm.v
        hand_r = face_r * 0.14
        hx = torso_w * 0.52
        hy = torso_y - torso_h * 0.10 - arm_lift * face_r * 0.22 + math.sin(t * 3.5) * (0.6 if self._speaking else 0.2)
        hand_color = QColor(220, 200, 185, 220) if self._theme == "dark" else QColor(180, 145, 130, 210)
        painter.setBrush(QBrush(hand_color))
        painter.drawEllipse(QPointF(center.x() - hx, hy), hand_r, hand_r)
        painter.drawEllipse(QPointF(center.x() + hx, hy), hand_r, hand_r)

        # Eyes
        eye_y = center.y() - face_r * 0.15 + nod * 1.5
        eye_dx = face_r * 0.22
        eye_r = face_r * 0.06 * (0.9 + 0.2 * (1.0 - stress))
        blink = 1.0 - _clamp(self._blink, 0.0, 1.0)  # 0=open, 1=closed -> invert
        blink = max(0.20, blink)

        eye_color = QColor(230, 230, 255) if self._theme == "dark" else QColor(30, 30, 50)
        painter.setBrush(QBrush(eye_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(center.x() - eye_dx, eye_y), eye_r, eye_r * blink)
        painter.drawEllipse(QPointF(center.x() + eye_dx, eye_y), eye_r, eye_r * blink)

        # Mouth (viseme-driven)
        mouth_y = center.y() + face_r * 0.18 + nod * 1.0
        mouth_w = face_r * 0.30
        mouth_h = face_r * (0.05 + 0.18 * self._mouth.v)
        curve = self._smile.v
        if self.emotion_tag == "stressed":
            curve = 0.15
        elif self.emotion_tag == "focused":
            curve = 0.25
        elif self.emotion_tag == "cheerful":
            curve = 0.60

        mouth_color = QColor(245, 210, 210, 220) if self._theme == "dark" else QColor(120, 60, 60, 210)
        painter.setBrush(QBrush(mouth_color))
        painter.drawRoundedRect(QRectF(center.x() - mouth_w, mouth_y - mouth_h / 2, mouth_w * 2, mouth_h), 8, 8)

        # Name + emotion label
        painter.setPen(QPen(text, 1))
        painter.setFont(QFont("Segoe UI", 10))
        label = f"Etherea • {self.emotion_tag}"
        if self.thinking:
            label += " • thinking…"
        painter.drawText(QRectF(card.left() + 18, card.top() + 12, card.width() - 36, 18), Qt.AlignLeft | Qt.AlignVCenter, label)
