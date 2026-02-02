from __future__ import annotations

from pathlib import Path
from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QApplication

from corund.app_runtime import user_data_dir
from corund.ei_engine import EIEngine
from corund.ui.main_window_v2 import EthereaMainWindowV2
from corund.signals import signals
if TYPE_CHECKING:
    from corund.voice_engine import VoiceEngine
from corund.voice_engine import get_voice_engine


class AppController(QObject):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self.window = EthereaMainWindowV2()
        self.ei_engine = EIEngine()
        self.voice_engine: Optional["VoiceEngine"] = None
        self._log_path = Path(user_data_dir()) / "etherea.log"

        self._connect_signals()

        self._heartbeat = QTimer(self)
        self._heartbeat.setInterval(250)
        self._heartbeat.timeout.connect(self._tick)

    def _connect_signals(self) -> None:
        try:
            signals.emotion_updated.connect(self.window.on_emotion_updated)
            signals.system_log.connect(self.window.log_ui)
            signals.system_log.connect(self._write_log)
        except Exception:
            pass

    def _tick(self) -> None:
        sync = getattr(self.window, "_sync_aurora_state", None)
        if callable(sync):
            sync()

    def start(self) -> None:
        self.ei_engine.start()
        self._heartbeat.start()
        self._log("✅ EI Engine started.")

        try:
            self.voice_engine = get_voice_engine()
            if self.voice_engine and getattr(self.voice_engine, "has_mic", False):
                self.voice_engine.start_command_loop()
                self._log("✅ Voice engine started.")
            else:
                self._log("🔇 Voice engine unavailable (no mic or missing deps).")
        except Exception as exc:
            self._log(f"⚠️ Voice engine init failed: {exc}")

    def shutdown(self) -> None:
        try:
            self._heartbeat.stop()
        except Exception:
            pass
        try:
            self.ei_engine.stop()
        except Exception:
            pass
        self._log("✅ Shutdown complete.")

    def _write_log(self, message: str) -> None:
        try:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            if not self._log_path.exists():
                self._log_path.touch()
            with self._log_path.open("a", encoding="utf-8") as f:
                f.write(message + "\n")
        except Exception:
            pass

    def _log(self, message: str) -> None:
        try:
            signals.system_log.emit(message)
        except Exception:
            self.window.log_ui(message)
