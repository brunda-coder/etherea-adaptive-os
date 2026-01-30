import os
from PySide6.QtWidgets import QVBoxLayout, QTreeView, QFileSystemModel, QHeaderView
from PySide6.QtCore import QDir
from corund.ui.panels import GlassPanel

class FileExplorerPanel(GlassPanel):
    """
    Project Explorer for the Agentic Workspace.
    """
    def __init__(self, title="Explorer", parent=None):
        super().__init__(title=title, parent=parent)
        
        self.model = QFileSystemModel()
        self.model.setRootPath(os.getcwd())
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(os.getcwd()))
        
        # UI Styling
        self.tree.setStyleSheet("background: transparent; color: #f8f8f2; border: none;")
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        
        # Hide header and unneeded columns
        self.tree.header().hide()
        for i in range(1, 4):
            self.tree.setColumnHidden(i, True)
            
        self.layout.addWidget(self.tree)

    def select_file(self, rel_path: str):
        full_path = os.path.join(os.getcwd(), rel_path)
        index = self.model.index(full_path)
        self.tree.setCurrentIndex(index)
        self.tree.scrollTo(index)
