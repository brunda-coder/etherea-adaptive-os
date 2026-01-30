from PySide6.QtWidgets import QTextEdit, QVBoxLayout
from PySide6.QtGui import QFont, QColor
from corund.ui.panels import GlassPanel
from corund.ui.highlighter import PythonHighlighter
from corund.tools.router import ToolRouter

class FunctionalCodePanel(GlassPanel):
    """
    Real Code Editor replacing the static mockup.
    """
    def __init__(self, title="Editor", parent=None):
        super().__init__(title=title, parent=parent)
        
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 11))
        self.editor.setStyleSheet("background: transparent; color: #f8f8f2; border: none;")
        self.editor.setAcceptRichText(False)
        
        self.highlighter = PythonHighlighter(self.editor.document())
        self.layout.addWidget(self.editor)
        
        # Load default file as demo
        self.load_file("main.py")

    def load_file(self, rel_path):
        content = ToolRouter.instance().read_file(rel_path)
        self.editor.setPlainText(content)

    def save_file(self, rel_path):
        content = self.editor.toPlainText()
        ToolRouter.instance().write_file(rel_path, content)
