from PySide6.QtCore import QThread, Signal
import logging

logger = logging.getLogger(__name__)

class AvatarWorker(QThread):
    """
    Worker thread to handle AvatarEngine calls asynchronously.
    Prevents UI freeze when generating responses.
    """
    response_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, avatar_engine, user_text: str):
        super().__init__()
        self.avatar_engine = avatar_engine
        self.user_text = user_text

    def run(self):
        try:
            # Blocking call runs here in background thread
            response = self.avatar_engine.speak(self.user_text)
            self.response_ready.emit(response)
        except Exception as e:
            logger.exception("AvatarWorker failed")
            self.error_occurred.emit(str(e))
