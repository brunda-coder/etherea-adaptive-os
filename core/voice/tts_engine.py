from __future__ import annotations

from dataclasses import dataclass

from corund.signals import signals


@dataclass
class TTSSettings:
    enabled: bool = True
    dramatic_mode: bool = False


class TTSEngine:
    def __init__(self) -> None:
        self.settings = TTSSettings()

    def set_enabled(self, enabled: bool) -> None:
        self.settings.enabled = enabled

    def set_dramatic_mode(self, enabled: bool) -> None:
        self.settings.dramatic_mode = enabled

    def speak(self, text: str, meta: dict | None = None) -> None:
        if not self.settings.enabled:
            return
        payload = meta or {}
        signals.tts_requested.emit(text, payload)
        signals.tts_started.emit(text, payload)
        # Stub: local TTS would happen here.
        signals.tts_finished.emit(text, payload)


_tts_engine: TTSEngine | None = None


def get_tts_engine() -> TTSEngine:
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TTSEngine()
    return _tts_engine
