from corund.ui.panels import PdfPanel
from corund.ui.editors import FunctionalCodePanel
from corund.ui.terminal import TerminalPanel
from corund.ui.explorer import FileExplorerPanel
from corund.ui.timeline import TimelinePanel

class WorkspaceWidget(QWidget):
    """
    Professional Workspace Grid Layout.
    Organizes modular functional panels for productivity.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)
        
        # 1. Left Column (Navigation & Timeline)
        self.explorer = FileExplorerPanel("Project Files")
        self.timeline = TimelinePanel("Agent Timeline")
        
        self.layout.addWidget(self.explorer, 0, 0, 1, 1) # Row 0, Col 0
        self.layout.addWidget(self.timeline, 1, 0, 1, 1) # Row 1, Col 0
        
        # 2. Center Column (Focus - Code Editor)
        self.code = FunctionalCodePanel("main.py — Editor")
        self.layout.addWidget(self.code, 0, 1, 2, 2) # Row 0, Col 1, Span 2 Rows, Span 2 Cols
        
        # 3. Right Column (References & Tools)
        self.pdf = PdfPanel("Specification.pdf")
        self.terminal = TerminalPanel("Console / Terminal")
        
        self.layout.addWidget(self.pdf, 0, 3, 1, 1)      # Row 0, Col 3
        self.layout.addWidget(self.terminal, 1, 3, 1, 1) # Row 1, Col 3
        
        # Column Stretch
        self.layout.setColumnStretch(0, 1) # Left
        self.layout.setColumnStretch(1, 2) # Center (Wider)
        self.layout.setColumnStretch(2, 2) # Center
        self.layout.setColumnStretch(3, 1) # Right
