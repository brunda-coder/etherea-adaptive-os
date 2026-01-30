from PySide6.QtCore import Qt, QPointF, QSize, QRectF
from PySide6.QtGui import QIcon, QPainter, QPen, QColor, QPixmap, QBrush, QPainterPath

class IconProvider:
    """
    Generates professional vector icons using QPainter.
    No emojis. No images. Pure purity.
    """
    
    @staticmethod
    def get_icon(name: str, size: int = 40, color: QColor = QColor(200, 240, 255), badge_count: int = 0) -> QIcon:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        qp = QPainter(pixmap)
        qp.setRenderHint(QPainter.Antialiasing, True)
        
        # Style
        stroke_width = 2.0
        pen = QPen(color)
        pen.setWidthF(stroke_width)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        qp.setPen(pen)
        qp.setBrush(Qt.NoBrush)
        
        # Center context
        c = size / 2
        r = size * 0.35 # Radius/Scale
        
        if name == "home":
             # Geometric House
             # Roof
             path = QPainterPath()
             path.moveTo(c - r, c - r*0.2)
             path.lineTo(c, c - r*1.2)
             path.lineTo(c + r, c - r*0.2)
             # Body
             path.lineTo(c + r, c + r)
             path.lineTo(c - r, c + r)
             path.closeSubpath()
             # Door
             path.moveTo(c - r*0.3, c + r)
             path.lineTo(c - r*0.3, c + r*0.3)
             path.lineTo(c + r*0.3, c + r*0.3)
             path.lineTo(c + r*0.3, c + r)
             qp.drawPath(path)
             
        elif name == "avatar":
            # Silhouette
            # Head
            qp.drawEllipse(QPointF(c, c - r*0.5), r*0.5, r*0.5)
            # Body (Arc)
            path = QPainterPath()
            path.arcMoveTo(QRectF(c - r, c, r*2, r*2.0), 30)
            path.arcTo(QRectF(c - r, c, r*2, r*2.0), 30, 120)
            qp.drawPath(path)
            
        elif name == "notifications":
            # Bell
            path = QPainterPath()
            # Bell cup
            path.moveTo(c, c - r)
            path.cubicTo(c + r*0.8, c - r*0.2, c + r, c + r*0.5, c + r, c + r*0.5)
            path.lineTo(c - r, c + r*0.5)
            path.cubicTo(c - r, c + r*0.5, c - r*0.8, c - r*0.2, c, c - r)
            # Clapper
            qp.drawPath(path)
            qp.drawArc(QRectF(c - r*0.2, c + r*0.3, r*0.4, r*0.4), 210, 120)
            
        elif name == "settings":
            # Gear
            qp.drawEllipse(QPointF(c, c), r*0.4, r*0.4)
            # Teeth (Line loop)
            for i in range(0, 360, 45):
                qp.save()
                qp.translate(c, c)
                qp.rotate(i)
                qp.drawLine(0, int(r*0.6), 0, int(r*0.9))
                qp.restore()
                
        elif name == "cmd":
            # Terminal >_
            path = QPainterPath()
            path.moveTo(c - r*0.6, c - r*0.4)
            path.lineTo(c - r*0.1, c)
            path.lineTo(c - r*0.6, c + r*0.4)
            qp.drawPath(path)
            # Underscore
            qp.drawLine(QPointF(c + r*0.1, c + r*0.4), QPointF(c + r*0.6, c + r*0.4))
            
        elif name == "workspace":
            # Grid layout
            # Draw 4 squares
            d = r * 0.8
            qp.drawRect(QRectF(c - d, c - d, d*0.9, d*0.9)) # TL
            qp.drawRect(QRectF(c + 0.1*d, c - d, d*0.9, d*0.9)) # TR
            qp.drawRect(QRectF(c - d, c + 0.1*d, d*0.9, d*0.9)) # BL
            qp.drawRect(QRectF(c + 0.1*d, c + 0.1*d, d*0.9, d*0.9)) # BR
            
        if name == "aurora":
            # Spark/Star
            path = QPainterPath()
            path.moveTo(c, c - r)
            path.cubicTo(c + r*0.1, c - r*0.1, c + r*0.1, c - r*0.1, c + r, c)
            path.cubicTo(c + r*0.1, c + r*0.1, c + r*0.1, c + r*0.1, c, c + r)
            path.cubicTo(c - r*0.1, c + r*0.1, c - r*0.1, c + r*0.1, c - r, c)
            path.cubicTo(c - r*0.1, c - r*0.1, c - r*0.1, c - r*0.1, c, c - r)
            qp.drawPath(path)

        # Draw Badge Overlay
        if badge_count > 0:
            # Badge Circle
            badge_size = 14
            bx = size - badge_size - 2
            by = 2
            
            qp.setPen(Qt.NoPen)
            qp.setBrush(QColor(255, 60, 60)) # Alert Red
            qp.drawEllipse(bx, by, badge_size, badge_size)
            
            # Badge Text
            qp.setPen(QColor(255, 255, 255))
            qp.setFont(QFont("Segoe UI", 8, QFont.Bold))
            txt = str(badge_count) if badge_count < 10 else "9+"
            qp.drawText(QRectF(bx, by, badge_size, badge_size), Qt.AlignCenter, txt)

        qp.end()
        return QIcon(pixmap)
