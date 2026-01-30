import math
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, Property, QEasingCurve, QPropertyAnimation
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath, QLinearGradient, QBrush

class HoloPanel(QWidget):
    """
    Glass-morphic Holographic Panel for educational content.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 350)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True) # Interaction is via Avatar
        
        # Animation State
        self.step = 0 
        self.visual_step = 0.0 # Float for smooth transitions
        self.anim_t = 0.0 
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(30)
        
        # Fade Effect
        self._opacity_eff = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_eff)
        self._opacity = 0.0
        self._opacity_eff.setOpacity(0.0)

    def show_teaching_sequence(self):
        """Reset to start of sequence"""
        self.step = 0
        self.visual_step = 0.0
        self.anim_t = 0.0
        self._opacity_eff.setOpacity(0.0)
        self._fade_in()
        self.update()
        
    def next_step(self):
        """Manually advance (called by Avatar Gesture)"""
        if self.step < 4:
            self.step += 1
            # anim_t will reset in tick if needed, but here we just set the target
            self.update()

    def _fade_in(self):
        self.anim = QPropertyAnimation(self._opacity_eff, b"opacity")
        self.anim.setDuration(800)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def _tick(self):
        # 1. Step Interpolation (Moving Flow)
        s = 0.1 # Move towards current step
        self.visual_step = self.visual_step + (self.step - self.visual_step) * s
        
        # 2. Local animation within step
        self.anim_t += 0.04
        if self.anim_t > 1.0:
            self.anim_t = 1.0
        self.update()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        
        # Vivid Flow: Use visual_step to offset elements (Exaggerated)
        flow_offset = (self.visual_step - self.step) * 100.0 
        bob = math.sin(self.anim_t * 2.0) * 5.0
        
        w, h = self.width(), self.height()
        rect = QRectF(0, 0, w, h)
        
        # 1. Glass Pane Background
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor(10, 30, 40, 220))
        grad.setColorAt(1.0, QColor(5, 10, 15, 230))
        
        qp.setPen(QPen(QColor(0, 240, 255, 120), 1.5))
        qp.setBrush(grad)
        qp.drawRoundedRect(rect, 15, 15)
        
        qp.translate(flow_offset, bob) # Apply Moving & Bobbing Flow

        # 2. Content Logic (Smoothed)
        opacity = 1.0 - abs(self.visual_step - self.step)
        qp.setOpacity(max(0.1, opacity))
        if self.step == 0:
             # Panel 1: Title Card
             qp.setPen(QColor(0, 240, 255))
             qp.setFont(QFont("Segoe UI", 24, QFont.Bold))
             qp.drawText(rect, Qt.AlignCenter, "Regression Analysis")
             
             qp.setPen(QColor(200, 200, 200))
             qp.setFont(QFont("Segoe UI", 12))
             qp.drawText(QRectF(0, h/2 + 30, w, 30), Qt.AlignCenter, "Predicting trends from data")
             
        elif self.step >= 1:
            # Panels 2-4: Graph & Summary
            self._draw_graph(qp, w, h)
            
            if self.step == 4:
                # Panel 5: Summary Cards
                self._draw_summary(qp, w, h)

    def _draw_summary(self, qp: QPainter, w: int, h: int):
        cards = ["Goal: Prediction", "y = mx + c", "Minimize Error"]
        # Draw cards overlay at bottom
        card_w = 120
        spacing = 10
        total_w = len(cards) * card_w + (len(cards)-1)*spacing
        start_x = (w - total_w) / 2
        
        y_off = h - 60
        # Animation pop-up
        y_anim = y_off + (1.0 - self.anim_t) * 20
        
        for i, txt in enumerate(cards):
            r = QRectF(start_x + i*(card_w+spacing), y_anim, card_w, 40)
            
            qp.setBrush(QColor(20, 40, 60, 230))
            qp.setPen(QPen(QColor(0, 240, 255), 1))
            qp.drawRoundedRect(r, 8, 8)
            
            qp.setPen(QColor(255, 255, 255))
            qp.setFont(QFont("Segoe UI", 9, QFont.Bold))
            qp.drawText(r, Qt.AlignCenter, txt)

    def _draw_graph(self, qp: QPainter, w: int, h: int):
        # Margins
        mx, my = 40, 60
        gw, gh = w - 80, h - 120 # Leave room for summary
        
        # Header
        qp.setPen(QColor(0, 240, 255))
        qp.setFont(QFont("Segoe UI", 12, QFont.Bold))
        qp.drawText(QRectF(0, 15, w, 30), Qt.AlignCenter, "LINEAR REGRESSION MODEL")
        
        # Axes
        qp.setPen(QPen(QColor(255, 255, 255, 100), 2))
        qp.drawLine(mx, my+gh, mx+gw, my+gh) # X
        qp.drawLine(mx, my, mx, my+gh)       # Y
        
        # Data Points (Scatter)
        points = [
            (0.1, 0.2), (0.2, 0.3), (0.3, 0.25), (0.4, 0.5), 
            (0.5, 0.45), (0.6, 0.7), (0.7, 0.65), (0.8, 0.85), (0.9, 0.9)
        ]
        
        # Animate points appearing (Step 1)
        progress = 1.0 if self.step > 1 else self.anim_t
        points_to_show = int(len(points) * float(progress))
        
        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor(0, 240, 255))
        
        for i in range(points_to_show):
            px, py = points[i]
            x = mx + px * gw
            y = (my+gh) - py * gh
            qp.drawEllipse(QPointF(x, y), 5, 5)
            
        # Step 2: Regression Line
        if self.step >= 2:
            progress = 1.0 if self.step > 2 else self.anim_t
            
            p1 = QPointF(mx, (my+gh) - 0.15 * gh)
            p2 = QPointF(mx + gw, (my+gh) - 0.9 * gh)
            
            curr_p2 = p1 + (p2 - p1) * progress
            
            pen = QPen(QColor(255, 100, 100))
            pen.setWidth(3)
            qp.setPen(pen)
            qp.drawLine(p1, curr_p2)

        # Step 3: Residuals
        if self.step >= 3:
            fade = 1.0 if self.step > 3 else self.anim_t
            qp.setPen(QPen(QColor(255, 255, 255, int(150 * fade)), 1, Qt.DashLine))
            
            for px, py in points:
                # Approx line y at this x
                line_y_norm = 0.15 + (px * (0.9 - 0.15))
                
                screen_x = mx + px * gw
                screen_y_pt = (my+gh) - py * gh
                screen_y_line = (my+gh) - line_y_norm * gh
                
                qp.drawLine(QPointF(screen_x, screen_y_pt), QPointF(screen_x, screen_y_line))
