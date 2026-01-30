import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtGui import QColor, QPalette
from corund.ui.avatar_heroine_widget import AvatarHeroineWidget

def main():
    app = QApplication(sys.argv)
    
    # Window setup
    window = QWidget()
    window.setWindowTitle("Avatar Debug")
    window.resize(600, 800)
    
    # Dark background to see the avatar clearly
    p = window.palette()
    p.setColor(QPalette.Window, QColor(10, 10, 20))
    window.setPalette(p)
    
    layout = QVBoxLayout(window)
    
    # Avatar Widget
    avatar = AvatarHeroineWidget()
    layout.addWidget(avatar)
    
    # Test Gesture
    from PySide6.QtCore import QTimer
    QTimer.singleShot(2000, lambda: print("Performing Summon..."))
    QTimer.singleShot(2000, avatar.summon)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
