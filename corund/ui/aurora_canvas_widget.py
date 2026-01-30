from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen, QBrush
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from corund.aurora_state import AuroraCanvasState


class AuroraCanvasWidget(QWidget):
    intent_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._state: AuroraCanvasState | None = None
        self.setMinimumHeight(220)
        self.setAutoFillBackground(False)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(18, 18, 18, 18)
        self._layout.setSpacing(10)

        self.header = QLabel("Aurora Canvas")
        self.header.setStyleSheet("font-size: 16px; font-weight: 700; color: #eaf0ff;")

        self.mode_label = QLabel("Mode: idle")
        self.workspace_label = QLabel("Workspace: --")
        self.session_label = QLabel("Session: --")
        self.attention_label = QLabel("Attention: --")
        self.last_saved_label = QLabel("Last saved: --")
        self.ei_label = QLabel("EI: --")

        for label in (
            self.mode_label,
            self.workspace_label,
            self.session_label,
            self.attention_label,
            self.last_saved_label,
            self.ei_label,
        ):
            label.setStyleSheet("color: #cfd6ff; font-size: 12px;")

        self.status_frame = QFrame()
        self.status_frame.setStyleSheet(
            "QFrame { background: rgba(18, 20, 32, 0.85); border: 1px solid #1f253d; border-radius: 12px; }"
        )
        status_layout = QVBoxLayout(self.status_frame)
        status_layout.setContentsMargins(12, 12, 12, 12)
        status_layout.addWidget(self.mode_label)
        status_layout.addWidget(self.workspace_label)
        status_layout.addWidget(self.session_label)
        status_layout.addWidget(self.attention_label)
        status_layout.addWidget(self.last_saved_label)
        status_layout.addWidget(self.ei_label)

        self.actions_frame = QFrame()
        self.actions_frame.setStyleSheet(
            "QFrame { background: rgba(12, 14, 24, 0.9); border: 1px solid #1f253d; border-radius: 12px; }"
        )
        self.actions_layout = QVBoxLayout(self.actions_frame)
        self.actions_layout.setContentsMargins(10, 10, 10, 10)
        self.actions_layout.setSpacing(6)

        self.overlay_label = QLabel("")
        self.overlay_label.setAlignment(Qt.AlignCenter)
        self.overlay_label.setStyleSheet(
            "color: rgba(255, 220, 180, 0.9); font-weight: 700; font-size: 13px;"
        )

        self.warning_label = QLabel("")
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setStyleSheet(
            "color: rgba(255, 120, 120, 0.9); font-weight: 700; font-size: 12px;"
        )

        self.actions_opacity = QGraphicsOpacityEffect(self.actions_frame)
        self.actions_frame.setGraphicsEffect(self.actions_opacity)
        self.status_opacity = QGraphicsOpacityEffect(self.status_frame)
        self.status_frame.setGraphicsEffect(self.status_opacity)

        self._layout.addWidget(self.header)
        self._layout.addWidget(self.status_frame)
        self._layout.addWidget(self.actions_frame)
        self._layout.addWidget(self.overlay_label)
        self._layout.addWidget(self.warning_label)

    def apply_state(self, state: AuroraCanvasState) -> None:
        self._state = state
        self.mode_label.setText(f"Mode: {state.current_mode} | Layout: {state.layout_density}")
        workspace_text = state.workspace_name or "--"
        self.workspace_label.setText(f"Workspace: {workspace_text}")
        session_text = "active" if state.session_active else "inactive"
        self.session_label.setText(f"Session: {session_text}")
        self.attention_label.setText(f"Attention: {state.attention_level}")
        last_saved = state.last_saved or "--"
        self.last_saved_label.setText(f"Last saved: {last_saved}")
        self.ei_label.setText(
            f"EI: focus {state.focus:.2f} | stress {state.stress:.2f} | energy {state.energy:.2f}"
        )

        self._layout.setSpacing(state.spacing)
        self.status_opacity.setOpacity(state.nonessential_opacity)
        self.actions_opacity.setOpacity(state.nonessential_opacity)

        self.status_frame.setVisible(state.panel_visibility.get("status", True))
        self.actions_frame.setVisible(state.panel_visibility.get("actions", True))
        self.overlay_label.setText(state.overlay_text)
        self.warning_label.setText(state.warning_text)

        self._render_actions(state)
        self.update()

    def _render_actions(self, state: AuroraCanvasState) -> None:
        while self.actions_layout.count():
            item = self.actions_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        for action in state.suggested_actions:
            btn = QPushButton(action.label)
            btn.setEnabled(action.enabled)
            btn.setStyleSheet(
                "QPushButton { background: #1a1f34; border: 1px solid #2a3353; color: #e6ecff; padding: 6px; border-radius: 6px; }"
                "QPushButton:disabled { color: #6a6f88; background: #141725; }"
            )
            btn.clicked.connect(lambda _, action_id=action.action_id: self.intent_requested.emit(action_id))
            self.actions_layout.addWidget(btn)

        if not state.suggested_actions:
            empty = QLabel("No actions available")
            empty.setStyleSheet("color: #6f7aa8; font-size: 11px;")
            self.actions_layout.addWidget(empty)
import math
import random
from PySide6.QtCore import Qt, QTimer, QPoint, QPointF, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen, QBrush
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from corund.state import AppState

class AuroraCanvasWidget(QWidget):
    """
    Primary living surface.
    - Centered Aurora Ring.
    - Responsive to AppState (mode/EI).
    - Smooth pulse animation.
    """
    # Legacy signal for backward compatibility with main_window_v2
    intent_requested = Signal(str)

    # Theme Definitions (Top, Bot, Grid, Particle)
    THEMES = {
        "focus": {
            "top": QColor(5, 8, 15), "bot": QColor(2, 2, 5), 
            "grid": QColor(0, 240, 255, 40), "part": QColor(100, 220, 255, 180)
        },
        "study": {
            "top": QColor(10, 15, 40), "bot": QColor(5, 5, 15),  # Deep Blue
            "grid": QColor(80, 100, 255, 40), "part": QColor(150, 180, 255, 180)
        },
        "creative": {
            "top": QColor(25, 5, 20), "bot": QColor(10, 0, 5),   # Velvet/Purple
            "grid": QColor(255, 0, 150, 40), "part": QColor(255, 100, 200, 180)
        },
        "night": {
            "top": QColor(5, 5, 5), "bot": QColor(0, 0, 0),      # Monochrome
            "grid": QColor(100, 100, 100, 30), "part": QColor(150, 150, 150, 100)
        },
        "idle": {
             "top": QColor(8, 10, 14), "bot": QColor(3, 4, 6),
             "grid": QColor(100, 130, 160, 20), "part": QColor(255, 255, 255, 100)
        },
        "break": { # Added for completeness, though not explicitly in the prompt's THEMES
            "top": QColor(10, 8, 5), "bot": QColor(0, 0, 0),
            "grid": QColor(255, 160, 50, 30), "part": QColor(255, 180, 100, 180)
        }
    }

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

        self._state = None
        self._frame = 0 # Animation Loop
        
        # Color State (Start at Idle)
        self.target_key = "idle"
        self.cur_colors = self.THEMES["idle"].copy()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(30) # ~33 FPS

        # Subscribe to State
        self.state = AppState.instance()
        
        # Audio Engine
        from corund.music import MusicEngine
        self.music = MusicEngine.instance()
        self.spectrum = {'bass': 0.0, 'mid': 0.0, 'high': 0.0}
        self.music.spectrum_updated.connect(self.update_spectrum)
        
        # Visual Params
        self.mode = "idle"
        
        # Overlay Labels (Floating)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 20, 20, 20)
        self._layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        
        self.label_mode = QLabel("IDLE")
        self.label_mode.setStyleSheet("color: rgba(255,255,255,0.4); font-weight: bold; font-size: 12px; letter-spacing: 2px;")
        self._layout.addWidget(self.label_mode)

    def set_theme(self, name: str):
        """Transition to a new color theme."""
        if name in self.THEMES:
            self.target_key = name

    def apply_state(self, state) -> None:
        """Legacy API."""
        self._state = state

    def _lerp_color(self, c1: QColor, c2: QColor, t: float) -> QColor:
        r = c1.red() + (c2.red() - c1.red()) * t
        g = c1.green() + (c2.green() - c1.green()) * t
        b = c1.blue() + (c2.blue() - c1.blue()) * t
        a = c1.alpha() + (c2.alpha() - c1.alpha()) * t
        return QColor(int(r), int(g), int(b), int(a))

    def _tick(self):
        self._frame += 1
        
        # Sync simple local state with AppState
        current_mode = self.state.mode
        if self.mode != current_mode:
            self.mode = current_mode
            self.label_mode.setText(current_mode.upper())
            # Auto-switch theme based on mode if default
            if current_mode in self.THEMES and self.target_key not in ["study", "creative", "night"]: 
                 self.target_key = current_mode

        # Smooth Color Lerp
        tgt = self.THEMES.get(self.target_key, self.THEMES["idle"])
        
        lf = 0.05 
        for k in ["top", "bot", "grid", "part"]:
            self.cur_colors[k] = self._lerp_color(self.cur_colors[k], tgt[k], lf)
            
        self.update()

    def update_spectrum(self, spec: dict):
        self.spectrum = spec

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        if self._state:
            mood = self._state.theme_profile.get("emotion_tag", "calm")
            if mood in ("alert", "angry", "stressed"):
                gradient.setColorAt(0.0, QColor(42, 14, 20))
                gradient.setColorAt(1.0, QColor(16, 6, 10))
            elif mood in ("joy", "happy"):
                gradient.setColorAt(0.0, QColor(22, 26, 48))
                gradient.setColorAt(1.0, QColor(12, 16, 32))
            else:
                gradient.setColorAt(0.0, QColor(12, 16, 30))
                gradient.setColorAt(1.0, QColor(8, 10, 20))
        else:
            gradient.setColorAt(0.0, QColor(12, 16, 30))
            gradient.setColorAt(1.0, QColor(8, 10, 20))

        painter.fillRect(rect, QBrush(gradient))

        if self._state:
            ring_color = QColor(90, 180, 255, 180)
            if self._state.current_mode == "focus":
                ring_color = QColor(255, 200, 80, 200)
            elif self._state.current_mode == "break":
                ring_color = QColor(120, 220, 180, 180)
            elif self._state.current_mode == "blocked":
                ring_color = QColor(160, 160, 160, 150)
            elif self._state.current_mode == "error":
                ring_color = QColor(255, 120, 120, 180)

            pen = QPen(ring_color, 3)
            painter.setPen(pen)
            center = rect.center()
            base_radius = min(rect.width(), rect.height()) * 0.35
            attention_scale = {
                "low": 0.92,
                "med": 1.0,
                "high": 1.08,
            }.get(self._state.attention_level, 1.0)
            radius = base_radius * attention_scale
            painter.drawEllipse(center, radius, radius)

        painter.end()
        w, h = rect.width(), rect.height()
        
        # 1. Background Fill (Interpolated)
        bg_top = self.cur_colors["top"]
        bg_bot = self.cur_colors["bot"]

        # Audio Reactivity: Flash background on heavy bass
        bass = self.spectrum.get('bass', 0.0)
        if bass > 0.5:
            # Add some energy to the background
            bg_top = QColor(
                min(255, bg_top.red() + int(bass * 40)),
                min(255, bg_top.green() + int(bass * 20)),
                min(255, bg_top.blue() + int(bass * 60))
            )

        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, bg_top)
        grad.setColorAt(1.0, bg_bot)
        painter.fillRect(rect, grad)

        # 2. Perspective Grid (The "Lab" Floor)
        self._draw_grid(painter, w, h)

        # 3. Floating Data Particles (Holodeck)
        self._draw_particles(painter, w, h)

        painter.end()

    def _draw_grid(self, qp: QPainter, w: int, h: int):
        """Perspective grid to give depth."""
        # Theme Color
        if self.mode == "focus":
            grid_c = QColor(0, 240, 255, 40) # High-Tech Cyan
        elif self.mode == "break":
            grid_c = QColor(255, 160, 50, 30) # Warm Amber
        else:
            grid_c = QColor(100, 130, 160, 20) # Professional Slate
            
        # Audio: Grid pulse
        mid = self.spectrum.get('mid', 0.0)
        bass = self.spectrum.get('bass', 0.0)
        
        pulse_alpha = int(grid_c.alpha() * (1.0 + mid * 2.0))
        grid_c.setAlpha(min(255, pulse_alpha))

        pen = QPen(grid_c)
        pen.setWidth(1)
        qp.setPen(pen)

        # Horizon line (Bounce with bass)
        bounce = bass * 20.0
        horizon_y = h * 0.4 - bounce
        
        # Vertical lines (fan out)
        center_x = w / 2
        for i in range(-10, 11):
            offset = i * (w * 0.15)
            # Line from vanishing point (center_x, horizon_y) to bottom
            qp.drawLine(QPointF(center_x, horizon_y), QPointF(center_x + offset * 3, h))

        # Horizontal lines (get denser with distance)
        for i in range(1, 15):
            y_norm = 1.0 - (1.0 / (i * 0.4 + 1.0)) # exponential accumulation
            # map normalized 0..1 to horizon_y..h
            y = h - (y_norm * (h - horizon_y))
            qp.drawLine(QPointF(0, y), QPointF(w, y))

    def _draw_particles(self, qp: QPainter, w: int, h: int):
        """Floating data points / sparks."""
        # Initialize particles if needed
        if not hasattr(self, '_particles'):
            self._particles = []
            for _ in range(30):
                self._particles.append({
                    'x': random.random(),
                    'y': random.random(),
                    's': 0.5 + random.random() * 0.5, # speed
                    'z': random.random() # depth
                })

        # Physics
        speed_mult = 2.0 if self.mode == "focus" else 0.5
        if self.mode == "break": speed_mult = 0.2
        
        # Audio boost
        high = self.spectrum.get('high', 0.0)
        speed_mult += (high * 10.0) # Fast particles on hi-hats
        
        dt = 0.03 # assume 30fps
        
        particle_col = self.cur_colors["part"]
        
        qp.setPen(Qt.NoPen)
        qp.setBrush(particle_col)

        for p in self._particles:
            # Move up
            p['y'] -= p['s'] * dt * speed_mult
            # Reset
            if p['y'] < 0:
                p['y'] = 1.0
                p['x'] = random.random()

            # Render
            # transform 0..1 to screen
            px = p['x'] * w
            py = p['y'] * h
            size = 2.0 + p['z'] * 3.0 + (high * 4.0) # Pulse size
            
            # Simple fade at top/bottom
            alpha_mod = 1.0
            if p['y'] < 0.2: alpha_mod = p['y'] * 5.0
            if p['y'] > 0.8: alpha_mod = (1.0 - p['y']) * 5.0
            
            c = QColor(particle_col)
            c.setAlpha(min(255, int(c.alpha() * alpha_mod)))
            qp.setBrush(c)
            
            qp.drawEllipse(QPointF(px, py), size, size)
