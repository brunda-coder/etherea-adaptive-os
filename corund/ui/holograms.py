import math
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import QTimer, Qt, QPointF
from PySide6.QtGui import QPainter, QRadialGradient, QColor, QBrush, QLinearGradient

class NebulaBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.t = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)  # 20 FPS for smooth breathing

    def animate(self):
        self.t += 0.1
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Deep Space Base
        painter.fillRect(self.rect(), QColor(10, 10, 18))

        # 2. Calculating the "Breathing" Pulse
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        # Pulse creates a value that goes up and down smoothly
        pulse = (math.sin(self.t) + 1) / 2  # Range 0.0 to 1.0

        # 3. Draw the Aurora/Nebula Gradient
        # We move the center slightly to make it feel organic
        grad_x = center_x + math.cos(self.t * 0.5) * 50
        grad_y = center_y + math.sin(self.t * 0.5) * 50
        
        radius = max(width, height) * (0.8 + (pulse * 0.1)) # Expands and contracts
        
        gradient = QRadialGradient(QPointF(grad_x, grad_y), radius)
        
        # Colors: Deep Purple -> Cyan -> Transparent
        gradient.setColorAt(0.0, QColor(80, 0, 255, 40))   # Core (Purple)
        gradient.setColorAt(0.5, QColor(0, 200, 255, 20))  # Mid (Cyan)
        gradient.setColorAt(1.0, QColor(10, 10, 18, 0))    # Edge (Fade)

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

class HolographicEffect(QGraphicsOpacityEffect):
    """Adds a subtle ghosting/glow effect to widgets"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpacity(0.85)
