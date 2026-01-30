from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QFont

from corund.ui.icon_provider import IconProvider

class SideDock(QWidget):
    """
    Minimalist Side Dock for Home Mode.
    Contains icon-only navigation buttons (Vector, No Emojis).
    """
    mode_requested = Signal(str) # "home", "avatar", "notifications", "settings"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(80)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 15, 20, 0.95); /* Matte Black Enterprise */
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                padding: 12px;
                margin: 4px;
            }
            QPushButton:hover {
                background-color: rgba(0, 240, 255, 0.08); /* Subtle Cyan */
                border: 1px solid rgba(0, 240, 255, 0.15);
            }
            QPushButton:pressed {
                background-color: rgba(0, 240, 255, 0.15);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 30, 10, 20)
        layout.setSpacing(12)

        # 1. Home
        self.btn_home = self._create_btn("home", "Home")
        self.btn_home.clicked.connect(lambda: self.mode_requested.emit("home"))
        layout.addWidget(self.btn_home)
        
        # 2. Workspace
        self.btn_work = self._create_btn("workspace", "Workspace")
        self.btn_work.clicked.connect(lambda: self.mode_requested.emit("workspace"))
        layout.addWidget(self.btn_work)
        
        # 3. Avatar Mode
        self.btn_avatar = self._create_btn("avatar", "Avatar Mode")
        self.btn_avatar.clicked.connect(lambda: self.mode_requested.emit("avatar"))
        layout.addWidget(self.btn_avatar)
        
        # 4. Aurora Canvas
        self.btn_aurora = self._create_btn("aurora", "Aurora Canvas")
        self.btn_aurora.clicked.connect(lambda: self.mode_requested.emit("aurora"))
        layout.addWidget(self.btn_aurora)

        # 5. Ethera Command
        self.btn_cmd = self._create_btn("cmd", "Ethera Command")
        self.btn_cmd.clicked.connect(lambda: self.mode_requested.emit("cmd"))
        layout.addWidget(self.btn_cmd)
        
        # Spacer
        layout.addStretch(1)

        # 6. Notifications
        self.btn_notif = self._create_btn("notifications", "Notifications")
        self.btn_notif.clicked.connect(lambda: self.mode_requested.emit("notifications"))
        layout.addWidget(self.btn_notif)
        
        # 7. Settings
        self.btn_settings = self._create_btn("settings", "Settings")
        self.btn_settings.clicked.connect(lambda: self.mode_requested.emit("settings"))
        layout.addWidget(self.btn_settings)

        # Store buttons
        self.buttons = {"notifications": self.btn_notif}
        
        # Connect to Notifications
        from corund.notifications import NotificationManager
        self.notif_manager = NotificationManager.instance()
        self.notif_manager.notification_added.connect(self.update_notifications_icon)
        self.notif_manager.notifications_cleared.connect(self.update_notifications_icon)

    def update_notifications_icon(self):
        count = self.notif_manager.get_count()
        btn = self.buttons.get("notifications")
        if btn:
            btn.setIcon(IconProvider.get_icon("notifications", 40, badge_count=count))

    def _create_btn(self, icon_name, tooltip):
        btn = QPushButton()
        btn.setToolTip(tooltip)
        icon = IconProvider.get_icon(icon_name, 40)
        btn.setIcon(icon)
        btn.setIconSize(QSize(32, 32))
        return btn
