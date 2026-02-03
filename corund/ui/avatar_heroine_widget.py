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
    from corund.voice_engine import g_voice_engine
except Exception:
    g_voice_engine = None


def _clamp(x: float, a: float, b: float) -> float:
    return a if x < a else (b if x > b else x)


@dataclass
class _Anim:
    """Simple critically damped animator."""
    v: float
    target: float
    vel: float = 0.0

    def step(self, dt: float, stiffness: float = 18.0, damping: float = 0.85) -> None:
        err = self.target - self.v
        self.vel += err * stiffness * dt
        self.vel *= damping
        self.v += self.vel * dt


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
        self._accent_a = a
        self._accent_b = b
        self.update()

    def set_ei_state(self, focus: float, stress: float, energy: float, curiosity: Optional[float] = None) -> None:
        self.ei["focus"] = _clamp(float(focus), 0.0, 1.0)
        self.ei["stress"] = _clamp(float(stress), 0.0, 1.0)
        self.ei["energy"] = _clamp(float(energy), 0.0, 1.0)
        if curiosity is not None:
            self.ei["curiosity"] = _clamp(float(curiosity), 0.0, 1.0)
        self.update()

    def set_mode(self, mode: str) -> None:
        self.mode = (mode or "study").strip().lower()
        self.update()

    def set_emotion_tag(self, tag: str) -> None:
        self.emotion_tag = (tag or "calm").strip().lower()
        # Map emotion tags to smile targets
        if self.emotion_tag == "cheerful":
            self._smile.target = 0.65
        elif self.emotion_tag == "focused":
            self._smile.target = 0.25
        elif self.emotion_tag == "stressed":
            self._smile.target = 0.12
        else:
            self._smile.target = 0.35
        self.update()

    def pulse(self, strength: float = 1.0, duration: float = 0.35) -> None:
        now = time.time()
        self._pulse_amp = max(self._pulse_amp, _clamp(strength, 0.0, 1.5))
        self._pulse_until = max(self._pulse_until, now + max(0.05, float(duration)))

    # -------------------------
    # Internals
    # -------------------------
    def _hook_voice(self) -> None:
        if g_voice_engine is None:
            return
        try:
            # Voice engine can expose viseme and speaking state
            if hasattr(g_voice_engine, "on_viseme"):
                g_voice_engine.on_viseme = self._on_viseme  # type: ignore
            if hasattr(g_voice_engine, "on_speaking"):
                g_voice_engine.on_speaking = self._on_speaking  # type: ignore
        except Exception:
            pass

    def _on_viseme(self, v: float) -> None:
        self._mouth.target = _clamp(float(v), 0.0, 1.0)

    def _on_speaking(self, speaking: bool) -> None:
        self._speaking = bool(speaking)
        if speaking:
            self.pulse(0.9, 0.25)

    def _advance(self, now: float) -> None:
        dt = _clamp(now - self._last_ts, 0.0, 0.05)
        self._last_ts = now

        focus = self.ei.get("focus", 0.55)
        stress = self.ei.get("stress", 0.20)
        energy = self.ei.get("energy", 0.70)

        # Breath + tilt targets
        self._tilt.target = (0.5 - stress) * 0.25 + (0.5 - focus) * 0.12
        self._arm.target = 0.25 if self._speaking else 0.0

        # Blink schedule
        t = now - self._t0
        if t > self._blink_next:
            self._blink_t = 0.0
            self._blink_next = t + (2.2 + random.random() * 2.2)

        # Blink waveform (fast close, slower open)
        self._blink_t += dt
        if self._blink_t < 0.10:
            self._blink = _clamp(self._blink_t / 0.10, 0.0, 1.0)
        elif self._blink_t < 0.22:
            self._blink = _clamp(1.0 - (self._blink_t - 0.10) / 0.12, 0.0, 1.0)
        else:
            self._blink = 0.0

        # Pulse decay
        if now < self._pulse_until:
            amp = self._pulse_amp
        else:
            self._pulse_amp *= 0.92
            amp = self._pulse_amp

        # Expression tracking
        self._mouth.step(dt, stiffness=22.0, damping=0.80)
        self._smile.step(dt, stiffness=14.0, damping=0.86)
        self._tilt.step(dt, stiffness=10.0, damping=0.90)
        self._nod.step(dt, stiffness=18.0, damping=0.84)
        self._arm.step(dt, stiffness=12.0, damping=0.88)

        # Stress adds micro “wobble” to keep it alive
        if random.random() < 0.01 + 0.02 * stress:
            self._nod.vel += (0.5 + random.random()) * (0.7 + 0.6 * stress)

        # Energy boosts pulse a bit
        if random.random() < 0.006 + 0.01 * energy:
            self.pulse(0.5 + 0.6 * energy, 0.22)

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
        painter.setPen(QPen(border, 1))
        painter.setBrush(QBrush(panel))
        painter.drawRoundedRect(card, 18, 18)

        # Center stage
        cx = card.center().x()
        cy = card.center().y() - 6

        focus = self.ei.get("focus", 0.55)
        stress = self.ei.get("stress", 0.20)
        energy = self.ei.get("energy", 0.70)

        # Alive motion
        breath = 0.8 * math.sin(t * 1.6)
        tilt = self._tilt.v
        nod = self._nod.v

        base = min(card.width(), card.height()) * 0.34
        pulse = self._pulse_amp * (0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 6.0)))

        ring_r = base * (1.0 + 0.06 * pulse) * (0.98 + 0.02 * math.sin(t * 2.1))
        center = QPointF(cx + tilt * 6.0, cy + breath * 2.2 + nod * 3.0)

        # Ring colors
        a = QColor(*self._accent_a, 190 if self._theme == "dark" else 170)
        b = QColor(*self._accent_b, 40 if self._theme == "dark" else 55)

        # Glow ring (wide translucent)
        painter.setPen(QPen(b, 18 + 14 * energy + 18 * pulse, Qt.SolidLine, Qt.RoundCap))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, ring_r, ring_r)

        # Main ring
        painter.setPen(QPen(a, 6 + 6 * focus + 4 * pulse, Qt.SolidLine, Qt.RoundCap))
        painter.drawEllipse(center, ring_r, ring_r)

        # Face blob (screen)
        face_r = ring_r * 0.52
        if self._theme == "dark":
            face = QColor(25, 25, 35, 255)
        else:
            face = QColor(245, 245, 252, 255)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(face))
        painter.drawEllipse(center, face_r, face_r)

        # Torso
        torso_w = face_r * 1.6
        torso_h = face_r * 1.05
        torso_y = center.y() + face_r * 0.78 + breath * 1.0
        torso = QRectF(center.x() - torso_w / 2, torso_y - torso_h / 2, torso_w, torso_h)

        if self._theme == "dark":
            torso_color = QColor(20, 20, 32, 240)
        else:
            torso_color = QColor(230, 232, 245, 235)

        painter.setBrush(QBrush(torso_color))
        painter.drawRoundedRect(torso, 18, 18)

        # Hands
        arm_lift = self._arm.v
        hand_r = face_r * 0.14
        hx = torso_w * 0.52
        hy = torso_y - torso_h * 0.10 - arm_lift * face_r * 0.22 + math.sin(t * 3.5) * 0.2

        if self._theme == "dark":
            hand = QColor(220, 200, 185, 220)
        else:
            hand = QColor(190, 160, 140, 170)

        painter.setBrush(QBrush(hand))
        painter.drawEllipse(QPointF(center.x() - hx, hy), hand_r, hand_r)
        painter.drawEllipse(QPointF(center.x() + hx, hy), hand_r, hand_r)

        # Eyes — big LED panels with flowing highlights (reference style)
        eye_y = center.y() - face_r * 0.10 + nod * 1.5
        eye_dx = face_r * 0.23

        # Blink: _blink goes 0=open → 1=closed (we invert)
        blink = 1.0 - _clamp(self._blink, 0.0, 1.0)
        blink = max(0.12, blink)

        eye_w = face_r * 0.34
        eye_h = face_r * 0.26 * blink

        # Colors
        if self._theme == "dark":
            led = QColor(255, 230, 60, 235)      # bright yellow
            glow = QColor(255, 230, 60, 70)      # soft glow
            shine = QColor(255, 255, 255, 140)   # highlights
        else:
            led = QColor(240, 200, 40, 230)
            glow = QColor(240, 200, 40, 50)
            shine = QColor(255, 255, 255, 160)

        # Time-based flowing highlight (tiny movement so eyes feel "alive")
        flow = 0.5 + 0.5 * math.sin(t * 2.4)
        drift_x = (flow - 0.5) * eye_w * 0.10
        drift_y = (0.5 - flow) * eye_h * 0.14

        painter.setPen(Qt.NoPen)

        # Glow behind eyes
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(QPointF(center.x() - eye_dx, eye_y), eye_w * 0.70, eye_h * 0.80)
        painter.drawEllipse(QPointF(center.x() + eye_dx, eye_y), eye_w * 0.70, eye_h * 0.80)

        # Eye panels (rounded rectangles)
        painter.setBrush(QBrush(led))
        left_eye = QRectF(center.x() - eye_dx - eye_w / 2, eye_y - eye_h / 2, eye_w, eye_h)
        right_eye = QRectF(center.x() + eye_dx - eye_w / 2, eye_y - eye_h / 2, eye_w, eye_h)
        painter.drawRoundedRect(left_eye, 10, 10)
        painter.drawRoundedRect(right_eye, 10, 10)

        # Highlights (moving slightly = "flowing eyes")
        painter.setBrush(QBrush(shine))
        # top-left block
        painter.drawRoundedRect(
            QRectF(left_eye.left() + eye_w * 0.12 + drift_x, left_eye.top() + eye_h * 0.10 + drift_y,
                   eye_w * 0.30, eye_h * 0.28),
            6, 6
        )
        painter.drawRoundedRect(
            QRectF(right_eye.left() + eye_w * 0.12 + drift_x, right_eye.top() + eye_h * 0.10 + drift_y,
                   eye_w * 0.30, eye_h * 0.28),
            6, 6
        )
        # bottom-right dot
        painter.drawRoundedRect(
            QRectF(left_eye.left() + eye_w * 0.58 - drift_x, left_eye.top() + eye_h * 0.52 - drift_y,
                   eye_w * 0.22, eye_h * 0.22),
            6, 6
        )
        painter.drawRoundedRect(
            QRectF(right_eye.left() + eye_w * 0.58 - drift_x, right_eye.top() + eye_h * 0.52 - drift_y,
                   eye_w * 0.22, eye_h * 0.22),
            6, 6
        )

        # Mouth — tiny worried LED curve (matches reference)
        mouth_y = center.y() + face_r * 0.22 + nod * 1.0
        open_amt = _clamp(self._mouth.v, 0.0, 1.0)

        # Emotion curve: cheerful lifts, stressed droops
        mood = 0.0
        if self.emotion_tag == "stressed":
            mood = -1.0
        elif self.emotion_tag == "focused":
            mood = 0.2
        elif self.emotion_tag == "cheerful":
            mood = 0.7

        mouth_w = face_r * 0.18
        mouth_h = face_r * (0.025 + 0.06 * open_amt)

        if self._theme == "dark":
            mouth_color = QColor(255, 230, 80, 210)
        else:
            mouth_color = QColor(160, 120, 40, 210)

        pen = QPen(mouth_color, max(2, int(face_r * 0.035)))
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        x0 = center.x()
        y0 = mouth_y

        # Draw a small "m" using two arcs; mood shifts the curve up/down
        left_rect = QRectF(x0 - mouth_w * 0.90, y0 - mouth_h * 0.60, mouth_w * 0.90, mouth_h * 1.4)
        right_rect = QRectF(x0, y0 - mouth_h * 0.60, mouth_w * 0.90, mouth_h * 1.4)

        # mood shifts: cheerful -> less droop; stressed -> more droop
        offset = (1.0 - mood) * mouth_h * 0.35
        left_rect.translate(0, offset)
        right_rect.translate(0, offset)

        painter.drawArc(left_rect, 0 * 16, -180 * 16)
        painter.drawArc(right_rect, 0 * 16, -180 * 16)

        # Name + emotion label
        painter.setPen(QPen(text, 1))
        painter.setFont(QFont("Segoe UI", 10))
        label = f"Etherea • {self.emotion_tag}"
        if self.thinking:
            label += " • thinking…"
        painter.drawText(QRectF(card.left() + 18, card.top() + 12, card.width() - 36, 18),
                         Qt.AlignLeft | Qt.AlignVCenter, label)
