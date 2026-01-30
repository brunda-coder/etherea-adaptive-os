import sys
try:
    from PySide6.QtWidgets import QApplication, QWidget
except Exception:
    QApplication = None
    class QWidget:
        pass
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPainter, QColor


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 300)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.frame = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

    def paintEvent(self, event):
        print(f"DEBUG: Test paint event firing. Frame: {self.frame}")
        self.frame += 1
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # solid test circle
        painter.setBrush(QColor(0, 255, 255, 200))  # Semi-transparent Cyan
        painter.setPen(Qt.NoPen)
        cx = 150
        cy = 150 + int(10 * float(self.frame % 100) /
                       100.0)  # move it slightly
        painter.drawEllipse(QPoint(cx, cy), 50, 50)
        painter.end()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TestWindow()
    win.show()
    sys.exit(app.exec())
