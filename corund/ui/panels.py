from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont, QPainterPath, QLinearGradient

class GlassPanel(QWidget):
    """
    Base class for transparent, rounded, glass-morphic panels.
    """
    def __init__(self, title="Panel", parent=None):
        super().__init__(parent)
        self.title = title
        # Removed WA_TranslucentBackground to ensure stability, using paintEvent alpha instead
        self.setAttribute(Qt.WA_TranslucentBackground) 
        self.setMinimumSize(200, 150)
        
        # Shadow Effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)
        
        # Consistent Padding
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 40, 20, 20)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        w, h = rect.width(), rect.height()
        
        # 1. Background (Glass Gradient)
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor(40, 50, 70, 240))   # Lighter Top-Left
        grad.setColorAt(1.0, QColor(10, 15, 25, 250))   # Darker Bottom-Right
        
        qp.setBrush(grad)
        # Subtle Cyan Border
        qp.setPen(QPen(QColor(0, 240, 255, 60), 1.5))
        
        # Draw with slight inset for shadow space if needed, 
        # but GraphicsEffect handles shadow outside.
        qp.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 12, 12)
        
        # 2. Title
        qp.setPen(QColor(255, 255, 255, 200)) # Brighter Text
        qp.setFont(QFont("Segoe UI", 10, QFont.Bold))
        qp.drawText(QRectF(20, 15, w-40, 20), Qt.AlignLeft | Qt.AlignVCenter, self.title.upper())
        
        # 3. Separator (Gradient Line)
        l_grad = QLinearGradient(20, 38, w-20, 38)
        l_grad.setColorAt(0.0, QColor(0, 240, 255, 0))
        l_grad.setColorAt(0.5, QColor(0, 240, 255, 100))
        l_grad.setColorAt(1.0, QColor(0, 240, 255, 0))
        
        qp.setPen(QPen(QBrush(l_grad), 1))
        qp.drawLine(20, 38, w-20, 38)
        
        qp.end()

class NotesPanel(GlassPanel):
    def paintEvent(self, event):
        super().paintEvent(event)
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        
        # Draw lines
        qp.setPen(QPen(QColor(255, 255, 255, 15), 1))
        line_h = 30
        start_y = 60
        while start_y < self.height() - 20:
            qp.drawLine(20, start_y, self.width()-20, start_y)
            start_y += line_h
        qp.end()

class TaskPanel(GlassPanel):
    def paintEvent(self, event):
        super().paintEvent(event)
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        
        tasks = ["Review Q1 Roadmap", "Optimize Render Loop", "Update Neural Weights", "Sync with Cloud"]
        y = 60
        qp.setFont(QFont("Segoe UI", 11))
        
        for t in tasks:
            # Checkbox
            qp.setPen(QPen(QColor(0, 240, 255, 100), 1.5))
            qp.setBrush(Qt.NoBrush)
            qp.drawRoundedRect(20, y, 16, 16, 4, 4)
            
            # Text
            qp.setPen(QColor(220, 230, 255))
            qp.drawText(50, y+13, t)
            
            y += 40
        qp.end()

class CodePanel(GlassPanel):
    def paintEvent(self, event):
        super().paintEvent(event)
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setFont(QFont("Consolas", 10))
        
        lines = [
            ("def optimize_network(self):", "#f0a0f0"),
            ("    # Neural sync", "#708090"),
            ("    weights = self.get_weights()", "#d0d0d0"),
            ("    delta = weights * 0.05", "#d0d0d0"),
            ("    return self.apply(delta)", "#d0d0d0"),
            ("", ""),
            ("class Canvas(QWidget):", "#f0a0f0"),
            ("    def __init__(self):", "#f0a0f0"),
            ("        super().__init__()", "#d0d0d0")
        ]
        
        y = 60
        for text, col_hex in lines:
            if not text:
                y += 20
                continue
            qp.setPen(QColor(col_hex))
            qp.drawText(20, y, text)
            y += 20
        qp.end()

class PdfPanel(GlassPanel):
    def paintEvent(self, event):
        super().paintEvent(event)
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        
        # Draw placeholder rect (Thumbnail)
        margin = 30
        rect_w = self.width() - 2*margin
        rect_h = self.height() - 80
        
        qp.setBrush(QColor(255, 255, 255, 10))
        qp.setPen(Qt.NoPen)
        qp.drawRoundedRect(margin, 60, rect_w, rect_h, 8, 8)
        
        # Icon center
        qp.setPen(QColor(255, 255, 255, 30))
        qp.drawText(QRectF(margin, 60, rect_w, rect_h), Qt.AlignCenter, "PDF PREVIEW")
        qp.end()

class ActivityPanel(GlassPanel):
    def __init__(self, title="Session Activity", parent=None):
        super().__init__(title=title, parent=parent)
        self.cols = 12
        import random
        self.data = [random.random() for _ in range(self.cols)]

    def paintEvent(self, event):
        super().paintEvent(event)
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        
        bar_w = (self.width() - 40) / self.cols
        max_h = self.height() - 80
        
        qp.setBrush(QColor(0, 240, 255, 50))
        qp.setPen(Qt.NoPen)
        
        for i, val in enumerate(self.data):
            h = val * max_h
            x = 20 + i * bar_w + 2
            y = self.height() - 20 - h
            qp.drawRoundedRect(x, y, bar_w - 4, h, 2, 2)
        qp.end()
