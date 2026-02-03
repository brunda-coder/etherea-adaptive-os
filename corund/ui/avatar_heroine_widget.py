from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from PySide6.QtCore import Qt, QTimer, QPointF, QRectF
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPen,
    QPainterPath,
    QPixmap,
    QTransform,
)
from PySide6.QtWidgets import QWidget


def _clamp(x: float, a: float, b: float) -> float:
    return a if x < a else (b if x > b else x)


@dataclass
class _Anim:
    """Simple damped animator."""
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
    Screen-face avatar widget (2D stylized).

    ✅ Target look (your reference):
      - Big black screen face
      - Large glowing yellow eyes with moving highlights
      - Small worried mouth
      - Aura ring pulses with voice intensity (viseme)
      - Can render any image ("cartoon") inside the screen

    Voice sync in *this repo zip*:
      - corund/voice_engine.py exposes Qt signals:
          - speaking_state (bool)
          - viseme_updated (float)
      - We connect to those here.

    NOTE:
      - This is display-only. Actual "talking" audio is handled by VoiceEngine.
      - If no audio backend works, mouth/aura can still animate from viseme pump.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumHeight(260)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # EI state (used for subtle mood)
        self.ei: Dict[str, float] = {"focus": 0.55, "stress": 0.20, "energy": 0.70, "curiosity": 0.55}
        self.mode: str = "study"
        self.emotion_tag: str = "calm"
        self.thinking: bool = False

        # Theme/accent (kept, but face screen stays black like your reference)
        self._theme: str = "dark"
        self._accent_a: Tuple[int, int, int] = (160, 120, 255)
        self._accent_b: Tuple[int, int, int] = (255, 210, 120)

        # Animation clock
        self._t0 = time.time()
        self._last_ts = self._t0

        # Expression channels
        self._mouth = _Anim(0.10, 0.10)     # 0..1
        self._smile = _Anim(0.18, 0.18)     # 0..1 (used as mood curve)

        # Alive motion
        self._tilt = _Anim(0.0, 0.0)        # -1..1
        self._nod = _Anim(0.0, 0.0)         # 0..1 impulse
        self._arm = _Anim(0.0, 0.0)         # 0..1 lift

        # Blink timing
        self._blink = 0.0
        self._blink_t = 0.0
        self._blink_next = 2.2 + random.random() * 2.2

        # Voice-driven aura intensity
        self._voice_amp = _Anim(0.0, 0.0)   # viseme -> aura
        self._speaking = False

        # Display overlay (for "any cartoon" inside the screen)
        self._display_pixmap: Optional[QPixmap] = None
        self._display_mode: str = "face"  # "face" or "image"

        # Hook voice signals (fixed for your repo zip)
        self._hook_voice_signals()

        # Render loop
        self._timer = QTimer(self)
        self._timer.setInterval(16)  # ~60 fps
        self._timer.timeout.connect(self.update)
        self._timer.start()

    # -------------------------
    # Public API
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

        # Map emotion tags to a mouth curve target (subtle)
        if self.emotion_tag == "cheerful":
            self._smile.target = 0.45
        elif self.emotion_tag == "focused":
            self._smile.target = 0.22
        elif self.emotion_tag == "stressed":
            self._smile.target = 0.10
        else:
            self._smile.target = 0.18

        self.update()

    def pulse(self, strength: float = 1.0, duration: float = 0.25) -> None:
        # Legacy pulse helper – we now mainly use voice_amp, but keep this for events.
        self._voice_amp.target = max(self._voice_amp.target, _clamp(strength, 0.0, 1.5))

    # ✅ NEW: Render any image inside the face screen
    def set_display_image(self, image_path: str) -> bool:
        try:
            pm = QPixmap(image_path)
            if pm.isNull():
                return False
            self._display_pixmap = pm
            self._display_mode = "image"
            self.update()
            return True
        except Exception:
            return False

    def clear_display_image(self) -> None:
        self._display_pixmap = None
        self._display_mode = "face"
        self.update()

    # -------------------------
    # Voice signal hookup (repo-correct)
    # -------------------------
    def _hook_voice_signals(self) -> None:
        """
        Your zip uses Qt signals in VoiceEngine:
          - speaking_state: Signal(bool)
          - viseme_updated: Signal(float)
        """
        try:
            from corund.voice_engine import VoiceEngine
            ve = VoiceEngine.instance()

            if hasattr(ve, "speaking_state") and ve.speaking_state is not None:
                try:
                    ve.speaking_state.connect(self._on_speaking_state)  # type: ignore
                except Exception:
                    pass

            if hasattr(ve, "viseme_updated") and ve.viseme_updated is not None:
                try:
                    ve.viseme_updated.connect(self._on_viseme)  # type: ignore
                except Exception:
                    pass
        except Exception:
            # No voice engine available (CI/Termux) — we still render fine.
            pass

    def _on_speaking_state(self, speaking: bool) -> None:
        self._speaking = bool(speaking)
        if self._speaking:
            # spike aura slightly on speech start
            self._voice_amp.target = max(self._voice_amp.target, 0.65)

    def _on_viseme(self, v: float) -> None:
        vv = _clamp(float(v), 0.0, 1.0)
        # mouth opens based on viseme intensity
        self._mouth.target = vv
        # aura beats based on voice amplitude
        self._voice_amp.target = max(self._voice_amp.target, vv)

    # -------------------------
    # Animation stepping
    # -------------------------
    def _advance(self, now: float) -> None:
        dt = _clamp(now - self._last_ts, 0.0, 0.05)
        self._last_ts = now

        focus = self.ei.get("focus", 0.55)
        stress = self.ei.get("stress", 0.20)

        # micro tilt target (alive)
        self._tilt.target = (0.5 - stress) * 0.22 + (0.5 - focus) * 0.12
        self._arm.target = 0.25 if self._speaking else 0.0

        # blink schedule
        t = now - self._t0
        if t > self._blink_next:
            self._blink_t = 0.0
            self._blink_next = t + (2.2 + random.random() * 2.2)

        # blink waveform
        self._blink_t += dt
        if self._blink_t < 0.09:
            self._blink = _clamp(self._blink_t / 0.09, 0.0, 1.0)
        elif self._blink_t < 0.20:
            self._blink = _clamp(1.0 - (self._blink_t - 0.09) / 0.11, 0.0, 1.0)
        else:
            self._blink = 0.0

        # anim smoothing
        self._mouth.step(dt, stiffness=24.0, damping=0.80)
        self._smile.step(dt, stiffness=14.0, damping=0.86)
        self._tilt.step(dt, stiffness=10.0, damping=0.90)
        self._nod.step(dt, stiffness=18.0, damping=0.84)
        self._arm.step(dt, stiffness=12.0, damping=0.88)

        # voice amp decay (important: beat, then fall)
        self._voice_amp.step(dt, stiffness=16.0, damping=0.78)
        self._voice_amp.target *= 0.88
        if self._voice_amp.target < 0.02:
            self._voice_amp.target = 0.0

        # stress adds micro "wobble" nod
        if random.random() < 0.01 + 0.02 * stress:
            self._nod.vel += (0.5 + random.random()) * (0.7 + 0.6 * stress)

    def paintEvent(self, event) -> None:  # noqa: N802
        now = time.time()
        t = now - self._t0
        self._advance(now)

        w = float(self.width())
        h = float(self.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # glass card background
        if self._theme == "dark":
            panel = QColor(14, 14, 24, 190)
            border = QColor(60, 60, 90, 120)
            label_color = QColor(235, 235, 255, 220)
        else:
            panel = QColor(255, 255, 255, 210)
            border = QColor(40, 40, 60, 80)
            label_color = QColor(25, 25, 40, 220)

        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        card = QRectF(10, 10, w - 20, h - 20)
        painter.setPen(QPen(border, 1))
        painter.setBrush(QBrush(panel))
        painter.drawRoundedRect(card, 18, 18)

        # center stage
        cx = card.center().x()
        cy = card.center().y() - 6

        focus = self.ei.get("focus", 0.55)
        stress = self.ei.get("stress", 0.20)
        energy = self.ei.get("energy", 0.70)

        breath = 0.8 * math.sin(t * 1.6)
        tilt = self._tilt.v
        nod = self._nod.v

        base = min(card.width(), card.height()) * 0.34

        # ✅ Voice-beat aura pulse
        voice = _clamp(self._voice_amp.v, 0.0, 1.5)
        pulse = (0.25 + 0.75 * (0.5 + 0.5 * math.sin(t * 7.2))) * voice

        ring_r = base * (1.0 + 0.08 * pulse) * (0.98 + 0.02 * math.sin(t * 2.1))
        center = QPointF(cx + tilt * 6.0, cy + breath * 2.2 + nod * 3.0)

        # Aura colors
        a = QColor(*self._accent_a, 190 if self._theme == "dark" else 170)
        b = QColor(*self._accent_b, 55 if self._theme == "dark" else 70)

        # Glow ring
        painter.setPen(QPen(b, 18 + 10 * energy + 22 * pulse, Qt.SolidLine, Qt.RoundCap))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, ring_r, ring_r)

        # Main ring
        painter.setPen(QPen(a, 6 + 6 * focus + 6 * pulse, Qt.SolidLine, Qt.RoundCap))
        painter.drawEllipse(center, ring_r, ring_r)

        # Face screen (always black like your reference)
        face_r = ring_r * 0.52
        face = QColor(10, 10, 14, 255)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(face))
        painter.drawEllipse(center, face_r, face_r)

        # Torso + hands (kept as subtle silhouette)
        torso_w = face_r * 1.6
        torso_h = face_r * 1.05
        torso_y = center.y() + face_r * 0.78 + breath * 1.0
        torso = QRectF(center.x() - torso_w / 2, torso_y - torso_h / 2, torso_w, torso_h)

        torso_color = QColor(20, 20, 32, 240) if self._theme == "dark" else QColor(230, 232, 245, 235)
        painter.setBrush(QBrush(torso_color))
        painter.drawRoundedRect(torso, 18, 18)

        arm_lift = self._arm.v
        hand_r = face_r * 0.14
        hx = torso_w * 0.52
        hy = torso_y - torso_h * 0.10 - arm_lift * face_r * 0.22 + math.sin(t * 3.5) * 0.2
        hand = QColor(220, 200, 185, 220) if self._theme == "dark" else QColor(190, 160, 140, 170)
        painter.setBrush(QBrush(hand))
        painter.drawEllipse(QPointF(center.x() - hx, hy), hand_r, hand_r)
        painter.drawEllipse(QPointF(center.x() + hx, hy), hand_r, hand_r)

        # -------------------------
        # Face contents (rotate slightly with tilt = "orientation change")
        # -------------------------
        painter.save()

        # rotate around face center
        angle = tilt * 6.5 + math.sin(t * 0.9) * 0.6
        tr = QTransform()
        tr.translate(center.x(), center.y())
        tr.rotate(angle)
        tr.translate(-center.x(), -center.y())
        painter.setTransform(tr, True)

        # clip to face ellipse so "cartoon" stays inside screen
        clip = QPainterPath()
        clip.addEllipse(center, face_r * 0.985, face_r * 0.985)
        painter.setClipPath(clip)

        if self._display_mode == "image" and self._display_pixmap is not None and not self._display_pixmap.isNull():
            # ✅ any cartoon/image inside the screen
            pm = self._display_pixmap
            target = QRectF(center.x() - face_r, center.y() - face_r, face_r * 2, face_r * 2)

            # preserve aspect ratio
            src_w = pm.width()
            src_h = pm.height()
            if src_w > 0 and src_h > 0:
                scale = min(target.width() / src_w, target.height() / src_h)
                dw = src_w * scale
                dh = src_h * scale
                dst = QRectF(center.x() - dw / 2, center.y() - dh / 2, dw, dh)
                painter.drawPixmap(dst, pm, QRectF(0, 0, src_w, src_h))
        else:
            # ✅ Reference-style face: glowing eyes + tiny worried mouth

            # Eyes position
            eye_y = center.y() - face_r * 0.12 + nod * 1.5
            eye_dx = face_r * 0.23

            # blink factor
            blink = 1.0 - _clamp(self._blink, 0.0, 1.0)
            blink = max(0.12, blink)

            eye_w = face_r * 0.36
            eye_h = face_r * 0.28 * blink

            # Eye colors (yellow LED + glow + shine)
            led = QColor(255, 230, 60, 240)
            glow = QColor(255, 230, 60, 85)
            shine = QColor(255, 255, 255, 150)

            # Flowing highlights: drift a bit over time
            flow = 0.5 + 0.5 * math.sin(t * 2.6)
            drift_x = (flow - 0.5) * eye_w * 0.12
            drift_y = (0.5 - flow) * eye_h * 0.16

            painter.setPen(Qt.NoPen)

            # glow blobs behind eyes
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(QPointF(center.x() - eye_dx, eye_y), eye_w * 0.75, eye_h * 0.95)
            painter.drawEllipse(QPointF(center.x() + eye_dx, eye_y), eye_w * 0.75, eye_h * 0.95)

            # eye LED panels (rounded rects)
            painter.setBrush(QBrush(led))
            left_eye = QRectF(center.x() - eye_dx - eye_w / 2, eye_y - eye_h / 2, eye_w, eye_h)
            right_eye = QRectF(center.x() + eye_dx - eye_w / 2, eye_y - eye_h / 2, eye_w, eye_h)
            painter.drawRoundedRect(left_eye, 12, 12)
            painter.drawRoundedRect(right_eye, 12, 12)

            # highlights (reference-style blocks)
            painter.setBrush(QBrush(shine))

            # top-left highlight block
            painter.drawRoundedRect(
                QRectF(left_eye.left() + eye_w * 0.10 + drift_x, left_eye.top() + eye_h * 0.08 + drift_y,
                       eye_w * 0.32, eye_h * 0.30),
                8, 8
            )
            painter.drawRoundedRect(
                QRectF(right_eye.left() + eye_w * 0.10 + drift_x, right_eye.top() + eye_h * 0.08 + drift_y,
                       eye_w * 0.32, eye_h * 0.30),
                8, 8
            )

            # bottom-right dot highlight
            painter.drawRoundedRect(
                QRectF(left_eye.left() + eye_w * 0.60 - drift_x, left_eye.top() + eye_h * 0.52 - drift_y,
                       eye_w * 0.22, eye_h * 0.22),
                8, 8
            )
            painter.drawRoundedRect(
                QRectF(right_eye.left() + eye_w * 0.60 - drift_x, right_eye.top() + eye_h * 0.52 - drift_y,
                       eye_w * 0.22, eye_h * 0.22),
                8, 8
            )

            # Mouth: tiny worried "m" curve (opens slightly with viseme)
            mouth_y = center.y() + face_r * 0.24 + nod * 0.8
            open_amt = _clamp(self._mouth.v, 0.0, 1.0)

            # Mood shaping
            mood = 0.0
            if self.emotion_tag == "stressed":
                mood = -1.0
            elif self.emotion_tag == "focused":
                mood = 0.15
            elif self.emotion_tag == "cheerful":
                mood = 0.65

            mouth_w = face_r * 0.18
            mouth_h = face_r * (0.020 + 0.060 * open_amt)

            mouth_color = QColor(255, 230, 80, 220)
            pen = QPen(mouth_color, max(2, int(face_r * 0.035)))
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)

            x0 = center.x()
            y0 = mouth_y

            left_rect = QRectF(x0 - mouth_w * 0.90, y0 - mouth_h * 0.60, mouth_w * 0.90, mouth_h * 1.4)
            right_rect = QRectF(x0, y0 - mouth_h * 0.60, mouth_w * 0.90, mouth_h * 1.4)

            # cheerful -> less droop; stressed -> more droop
            offset = (1.0 - mood) * mouth_h * 0.35
            left_rect.translate(0, offset)
            right_rect.translate(0, offset)

            painter.drawArc(left_rect, 0 * 16, -180 * 16)
            painter.drawArc(right_rect, 0 * 16, -180 * 16)

        painter.restore()  # end face contents

        # Label
        painter.setPen(QPen(label_color, 1))
        painter.setFont(QFont("Segoe UI", 10))
        label = f"Etherea • {self.emotion_tag}"
        if self.thinking:
            label += " • thinking…"
        painter.drawText(
            QRectF(card.left() + 18, card.top() + 12, card.width() - 36, 18),
            Qt.AlignLeft | Qt.AlignVCenter,
            label,
)
