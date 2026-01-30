from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

class AppBubble(QPushButton):
    def __init__(self, parent, name, x, y, callback=None):
        super().__init__(parent)
        self.setText(name.upper()) # Force Uppercase for sci-fi look
        self.setGeometry(x, y, 100, 100)
        self.callback = callback
        
        self.clicked.connect(self.on_click)

        # 🎨 THE PURE GLASS LOOK (No Emojis)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 10);
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 50px; /* Perfectly Round */
                color: rgba(255, 255, 255, 0.9);
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 2px; /* Spaced out text */
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 25);
                border: 2px solid rgba(0, 240, 255, 200);
                color: white;
                box-shadow: 0 0 15px cyan;
            }
            QPushButton:pressed {
                background-color: rgba(0, 240, 255, 50);
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

    def on_click(self):
        if self.callback:
            self.callback(self.text())
