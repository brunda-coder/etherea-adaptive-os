from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer, QPoint, QRectF
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QBrush, QPen
import math
from corund.signals import signals


class AvatarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Dynamic sizing enabled
        self.state = {"focus": 0.5, "stress": 0.2}

        # Animation
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(30)  # 30ms ~ 33fps
        self.frame = 0

        # Connect signals
        signals.emotion_updated.connect(self.update_state)

        self.is_thinking = False

        # Starfield initialization
        import random
        self.stars = []
        for _ in range(40):
            self.stars.append({
                "x": random.randint(0, 320),
                "y": random.randint(0, 320),
                "s": random.uniform(0.2, 1.5),  # Smaller, subtler stars
                "speed": random.uniform(0.005, 0.02) # Slower movement
            })

        self.mouse_pos = QPoint(160, 160)
        self.setMouseTracking(True)

    def set_thinking(self, thinking: bool):
        self.is_thinking = thinking
        self.update()

    def update_state(self, state):
        self.state = state
        self.update()

    def update_animation(self):
        self.frame += 1
        self.update()

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()
        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        if self.width() <= 0 or self.height() <= 0:
            return

        painter = QPainter(self)
        if not painter.isActive():
            return

        painter.setRenderHint(QPainter.Antialiasing)

        # 0. Draw Starfield (Subtle Background)
        self.draw_starfield(painter)

        # State
        stress = self.state.get("stress", 0.2)
        breath_speed = 0.05 + (stress * 0.1)
        bob_amplitude = 10
        self.vertical_offset = math.sin(
            self.frame * breath_speed) * bob_amplitude

        # Centering
        cx = self.width() // 2
        cy = int(self.height() // 2 + self.vertical_offset)
        center = QPoint(cx, cy)

        # 1. Draw Aurora Ring
        self.draw_aurora_ring(painter, center)

        # 2. Draw Avatar Core
        self.draw_avatar_core(painter, center)

        # Update frame
        self.frame = (self.frame + 1) % 10000

        painter.end()

    def draw_starfield(self, painter):
        stress = self.state.get("stress", 0.2)
        for star in self.stars:
            # Stars move gracefully
            offset_x = math.sin(self.frame * star["speed"]) * 10
            offset_y = math.cos(self.frame * star["speed"]) * 10

            x = star["x"] + offset_x
            y = star["y"] + offset_y

            alpha = int(150 * star["s"]) # Slightly more transparent
            color = QColor(255, 255, 255, alpha)
            painter.setPen(QPen(color, star["s"]))
            painter.drawPoint(int(x) % self.width(), int(y) % self.height())
        painter.setPen(Qt.NoPen)

    def draw_aurora_ring(self, painter, center):
        focus = self.state.get("focus", 0.5)
        stress = self.state.get("stress", 0.2)

        # Mouse Proximity Lean
        dx = self.mouse_pos.x() - center.x()
        dy = self.mouse_pos.y() - center.y()
        dist = math.sqrt(dx*dx + dy*dy)
        if 0 < dist < 150:
            lean_x = (dx / dist) * (150 - dist) * 0.2
            lean_y = (dy / dist) * (150 - dist) * 0.2
            center = QPoint(int(center.x() + lean_x), int(center.y() + lean_y))
        elif dist == 0:
            pass  # No lean if exactly at center

        breath_speed = 0.05 + (stress * 0.1)

        # Liquid Motion / Radius Modulation
        def get_radius(angle):
            # Base radius
            if self.is_thinking:
                base = 85 + math.sin(self.frame * 0.2) * 10
            else:
                base = 80 + (focus * 20) + \
                    math.sin(self.frame * breath_speed) * 5

            # Deformation (Liquid feel)
            deformation = math.sin(angle * 3 + self.frame * 0.1) * 3
            deformation += math.cos(angle * 5 - self.frame * 0.05) * 2
            return base + deformation

        # Draw the ring using multiple segments for liquid look
        # Draw the ring using multiple segments for liquid look
        if stress > 0.6:
            # Warmer, less alarmist red
            color = QColor(255, 80, 80, 120)
            secondary_color = QColor(255, 120, 80, 60)
        elif focus > 0.7:
            # Golden focus
            color = QColor(255, 200, 100, 120)
            secondary_color = QColor(255, 220, 150, 60)
        else:
            # Ethereal Cyan/Blue
            color = QColor(0, 180, 255, 120)
            secondary_color = QColor(100, 200, 255, 60)

        # Draw outer glow glow
        painter.setPen(Qt.NoPen)
        for r_ext in range(10, 0, -2):
            alpha = int(20 * (r_ext / 10))
            glow_color = QColor(color.red(), color.green(),
                                color.blue(), alpha)
            painter.setBrush(QBrush(glow_color))

            # Simplified liquid glow (approximate with points or path)
            pts = []
            for a in range(0, 361, 10):
                angle_rad = math.radians(a)
                rad = get_radius(angle_rad) + r_ext
                pts.append(QPoint(int(center.x() + math.cos(angle_rad) * rad),
                                  int(center.y() + math.sin(angle_rad) * rad)))
            painter.drawPolygon(pts)

        # Main Ring Core
        painter.setBrush(QBrush(color))
        pts = []
        for a in range(0, 361, 5):
            angle_rad = math.radians(a)
            rad = get_radius(angle_rad)
            pts.append(QPoint(int(center.x() + math.cos(angle_rad) * rad),
                              int(center.y() + math.sin(angle_rad) * rad)))
        painter.drawPolygon(pts)

        # Energy particles
        particle_count = 3 if stress < 0.5 else 6
        for i in range(particle_count):
            angle = (self.frame * (0.05 + stress * 0.1) +
                     i * (2 * math.pi / particle_count))
            base_r = get_radius(angle)
            px = center.x() + math.cos(angle) * (base_r * 0.9)
            py = center.y() + math.sin(angle) * (base_r * 0.9)
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.drawEllipse(QPoint(int(px), int(py)), 3, 3)

    def draw_avatar_core(self, painter, center):
        # Multi-layered core for depth
        focus = self.state.get("focus", 0.5)
        stress = self.state.get("stress", 0.2)

        # Outer core glow
        outer_grad = QRadialGradient(center, 60)
        outer_grad.setColorAt(0, QColor(255, 255, 255, 50))
        outer_grad.setColorAt(0.7, QColor(200, 240, 255, 30))
        outer_grad.setColorAt(1, Qt.transparent)
        painter.setBrush(QBrush(outer_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, 60, 60)

        # Middle layer - pulses with activity
        pulse_size = 45 + int(math.sin(self.frame * 0.1) * 3)
        mid_grad = QRadialGradient(center, pulse_size)
        mid_grad.setColorAt(0, QColor(255, 255, 255, 200))
        mid_grad.setColorAt(0.5, QColor(200, 240, 255, 150))
        mid_grad.setColorAt(1, Qt.transparent)
        painter.setBrush(QBrush(mid_grad))
        painter.drawEllipse(center, pulse_size, pulse_size)

        # Inner core - bright center
        inner_grad = QRadialGradient(center, 25)
        inner_grad.setColorAt(0, QColor(255, 255, 255, 255))
        inner_grad.setColorAt(0.5, QColor(255, 255, 255, 220))
        inner_grad.setColorAt(1, QColor(220, 240, 255, 100))
        painter.setBrush(QBrush(inner_grad))
        painter.drawEllipse(center, 25, 25)
