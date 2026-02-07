from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable

from core.voice import get_tts_engine
from corund.voice_engine import get_voice_engine


@dataclass
class VoiceState:
    voice_enabled: bool = True
    mic_enabled: bool = False
    sensitivity: float = 0.5
    backend: str = "auto"


class VoiceManager:
    def __init__(self) -> None:
        self.state = VoiceState()
        self.tts = get_tts_engine()
        self.engine = get_voice_engine()
        self._command_cb: Callable[[str], None] | None = None
        self._mic_thread: threading.Thread | None = None
        self._stop = threading.Event()

    @property
    def has_mic(self) -> bool:
        return bool(getattr(self.engine, "has_mic", False))

    def set_command_callback(self, cb: Callable[[str], None]) -> None:
        self._command_cb = cb

    def configure(self, *, voice_enabled: bool | None = None, mic_enabled: bool | None = None, sensitivity: float | None = None) -> None:
        if voice_enabled is not None:
            self.state.voice_enabled = bool(voice_enabled)
            self.tts.set_enabled(bool(voice_enabled))
        if mic_enabled is not None:
            self.state.mic_enabled = bool(mic_enabled)
            if mic_enabled:
                self.start_mic_stream()
        if sensitivity is not None:
            self.state.sensitivity = max(0.0, min(1.0, float(sensitivity)))

    def speak_demo(self, text: str = "Hello, I am Etherea. This is a lip sync demo.") -> None:
        if self.state.voice_enabled:
            self.tts.speak(text, {"source": "speak_demo"})

    def start_command_loop(self) -> None:
        try:
            self.engine.start_command_loop()  # type: ignore[attr-defined]
        except Exception:
            pass

    def start_mic_stream(self) -> None:
        if self._mic_thread and self._mic_thread.is_alive():
            return
        self._stop.clear()
        self._mic_thread = threading.Thread(target=self._mic_loop, daemon=True)
        self._mic_thread.start()

    def _mic_loop(self) -> None:
        while not self._stop.is_set() and self.state.mic_enabled:
            time.sleep(1.0)
            # Stub recognition pathway: wired + safe fallback when no ASR backend.
            if self._command_cb and self.state.sensitivity > 0.95:
                self._command_cb("open workspace")

    def shutdown(self) -> None:
        self._stop.set()
