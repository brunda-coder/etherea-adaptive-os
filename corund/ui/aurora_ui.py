import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox
from PySide6.QtCore import Qt
from .holograms import NebulaBackground
from .bubbles import AppBubble

class AuroraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Etherea Aurora v4.0")
        self.setGeometry(100, 100, 1000, 600)
        
        self.nebula = NebulaBackground(self)
        self.setCentralWidget(self.nebula)

        self.title = QLabel("E T H E R E A", self.nebula)
        self.title.setGeometry(0, 50, 1000, 100)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 40px; color: rgba(255,255,255,0.8); font-weight: bold; letter-spacing: 12px;")

        self.status = QLabel("SYSTEM ONLINE", self.nebula)
        self.status.setGeometry(0, 500, 1000, 30)
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("color: rgba(0, 255, 255, 0.7); font-family: Consolas; font-size: 10px; letter-spacing: 3px;")

        # --- CLEAN BUBBLES (No Emojis) ---
        # Format: (parent, "NAME", x, y, callback)
        self.btn_term = AppBubble(self.nebula, "Terminal", 250, 250, self.launch_terminal)
        self.btn_files = AppBubble(self.nebula, "Data", 450, 250, self.launch_files)
        self.btn_avatar = AppBubble(self.nebula, "Avatar", 650, 250, self.launch_avatar)

    def launch_terminal(self, _):
        self.status.setText("ACCESSING MAINFRAME...")
        if os.name == 'nt': os.system('start cmd')

    def launch_files(self, _):
        self.status.setText("OPENING DATA CORE...")
        if os.name == 'nt': os.startfile('.')

    def launch_avatar(self, _):
        self.status.setText("AVATAR INTERFACE ACTIVE...")
        msg = QMessageBox()
        msg.setWindowTitle("Avatar")
        msg.setText("Visual interface not loaded. Voice module active. 🎤")
        msg.setStyleSheet("background-color: #0f0f1a; color: white;")
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuroraWindow()
    window.show()
    sys.exit(app.exec())
