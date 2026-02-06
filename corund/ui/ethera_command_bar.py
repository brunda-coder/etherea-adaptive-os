from PySide6.QtWidgets import QLineEdit


class HomeCommandInputController:
    """Voice-first entrypoint wrapper for home command input."""

    def __init__(self, app_controller=None):
        self.app_controller = app_controller

    def route_voice_command(self, text: str) -> dict:
        cmd = (text or "").strip()
        if not cmd:
            return {"ok": False, "reason": "empty"}
        if self.app_controller is not None:
            self.app_controller.execute_user_command(cmd, source="voice")
        return {"ok": True, "command": cmd}


class EthereaCommandBar(QLineEdit):
    """Visible home command input with voice-first controller path."""

    def __init__(self, parent=None, app_controller=None):
        super().__init__(parent)
        self.setPlaceholderText("Voice-first command input… (e.g., 'open workspace')")
        self.setStyleSheet(
            """
            QLineEdit {
                background: #11121a;
                color: #e8e8ff;
                border: 1px solid #2a3353;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                selection-background-color: #3d4b7a;
            }
            QLineEdit:focus {
                border: 1px solid #5a75cf;
                background: #151622;
            }
        """
        )
        self.controller = HomeCommandInputController(app_controller=app_controller)
        self.returnPressed.connect(self.process_command)

    def process_command(self):
        text = self.text().strip()
        if text:
            self.controller.route_voice_command(text)
        self.clear()


EtheraCommandBar = EthereaCommandBar
