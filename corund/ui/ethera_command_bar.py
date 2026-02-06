from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt, Signal
from corund.state import AppState

class EthereaCommandBar(QLineEdit):
    """
    Top command bar for natural language control.
    Parses commands like 'focus mode', 'break', 'reset' and updates AppState.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Ask Etherea... (e.g., 'focus mode', 'take a break')")
        self.setStyleSheet("""
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
        """)
        self.returnPressed.connect(self.process_command)

    def process_command(self):
        text = self.text().strip().lower()
        if not text:
            return
        
        state = AppState.instance()
        
        # Simple NL parsing
        if text.startswith("say "):
            # Voice Command
            msg = text[4:].strip()
            from corund.voice import VoiceEngine
            VoiceEngine.instance().speak(msg)
            self.placeholder_feedback(f"🗣️ Speaking: {msg}")
        elif "music" in text or "play" in text:
            from corund.music import MusicEngine
            if "stop" in text:
                MusicEngine.instance().stop()
                self.placeholder_feedback(f"🛑 Music Stopped")
            else:
                MusicEngine.instance().play()
                self.placeholder_feedback(f"🎵 Playing Ambient Mix")
        elif "focus" in text:
            state.set_mode("focus", reason="user command")
            self.placeholder_feedback(f"⚡ Entering Focus Mode")
        elif "break" in text or "relax" in text:
            state.set_mode("break", reason="user command")
            self.placeholder_feedback(f"☕ Taking a Break")
        elif "idle" in text or "reset" in text:
            state.set_mode("idle", reason="user command")
            self.placeholder_feedback(f"🌱 Idling")
        else:
            # Fallback / Log
            print(f"Unknown command: {text}")
        
        self.clear()

    def placeholder_feedback(self, msg: str):
        """Show temporary feedback in placeholder."""
        self.setPlaceholderText(msg)
        # Restore default placeholder after delay could be added here, 
        # but for now we just leave the feedback until next type.


# Backward-compatible alias used by older windows.
EtheraCommandBar = EthereaCommandBar
