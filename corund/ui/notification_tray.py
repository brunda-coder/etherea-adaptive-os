from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from corund.ui.panels import GlassPanel
from corund.notifications import NotificationManager

class NotificationTray(GlassPanel):
    """
    Vertical tray displaying the list of notifications.
    Uses GlassPanel styling but optimized for a list view.
    """
    def __init__(self, parent=None):
        super().__init__(title="NOTIFICATIONS", parent=parent)
        self.resize(350, 600) # Default size, usually managed by layout
        
        # Remove default layout content margins from GlassPanel base if they conflict,
        # but here we'll just add to the existing layout.
        
        # Content Container
        self.content_widget = QWidget()
        self.content_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        self.content_layout.addStretch() # Push items up
        
        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.content_widget)
        # Transparent Scroll Area
        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                border: none;
                background: rgba(0,0,0,50);
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 240, 255, 50);
                border-radius: 3px;
            }
        """)
        
        # Add scroll to the GlassPanel layout
        self.layout.addWidget(self.scroll)
        
        # Connect
        self.manager = NotificationManager.instance()
        self.manager.notification_added.connect(self.refresh)
        self.manager.notifications_cleared.connect(self.refresh)
        
        self.refresh()

    def refresh(self):
        # Clear existing items (except stretch)
        while self.content_layout.count() > 1:
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        notifs = self.manager.get_all()
        
        if not notifs:
            lbl = QLabel("No new notifications.")
            lbl.setStyleSheet("color: rgba(255,255,255,100); font-style: italic;")
            lbl.setAlignment(Qt.AlignCenter)
            self.content_layout.insertWidget(0, lbl)
            return

        for n in notifs:
            item = self._create_item(n)
            self.content_layout.insertWidget(self.content_layout.count()-1, item)
            
    def _create_item(self, data):
        w = QWidget()
        w.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 10);
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 20);
            }
            QLabel { background: transparent; border: none; }
        """)
        l = QVBoxLayout(w)
        l.setContentsMargins(15, 12, 15, 12)
        l.setSpacing(4)
        
        title = QLabel(data["title"])
        title.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 13px;")
        
        msg = QLabel(data["message"])
        msg.setStyleSheet("color: #e0e0e0; font-size: 12px;")
        msg.setWordWrap(True)
        
        time = QLabel(data["timestamp"].strftime("%H:%M"))
        time.setStyleSheet("color: rgba(255,255,255,80); font-size: 10px;")
        time.setAlignment(Qt.AlignRight)
        
        l.addWidget(title)
        l.addWidget(msg)
        l.addWidget(time)
        return w
