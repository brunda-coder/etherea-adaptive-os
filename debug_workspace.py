from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from corund.ui.workspace_widget import WorkspaceWidget
from corund.ui.panels import GlassPanel
import sys

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.resize(1024, 768)
    window.setStyleSheet("background-color: #101520;") # Dark background

    # Container
    central = QWidget()
    layout = QVBoxLayout(central)
    window.setCentralWidget(central)

    # 1. Test Simple Glass Panel
    panel = GlassPanel("Test Panel")
    layout.addWidget(panel)

    # 2. Test Full Workspace
    workspace = WorkspaceWidget()
    layout.addWidget(workspace)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
