from __future__ import annotations

import os
import queue
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

# Qt is optional in some environments (CI / Termux).
try:
    from PySide6.QtCore import QObject, Signal
except Exception:
    class QObject:  # minimal stub
        pass
    def Signal(*a, **k):  # type: ignore
        return None  # noqa: ANN001

# Local adapters (safe, best-effort)
try:
    from corund.voice_adapters import speak_edge_tts, speak_pyttsx3, speak_openai_tts
except Exception:
    speak_edge_tts = None
    speak_pyttsx3 = None
    speak_openai_tts = None


def _env_key() -> Optional[str]:
    # Support the user's secret name, while keeping OpenAI defaults.
    return os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY2")


def _normalize_backend(x: str) -> str:
    x = (x or "").strip().lower()
    if x in ("openai", "oai", "gpt", "tts_openai"):
        return "openai"
    if x in ("edge", "msedge", "microsoft", "edge_tts"):
        return "edge"
    if x in ("pyttsx3", "local", "offline"):
        return "pyttsx3"
    if x in ("none", "off", "disabled"):
        return "none"
    return "auto"


def _estimate_duration(text: str) -> float:
    # very rough "reading time": ~12–15 chars/sec; clamp
    n = max(1, len(text.strip()))
    return max(0.8, min(18.0, n / 14.0))



_OPENAI_VOICES = {
    "alloy","ash","ballad","coral","echo","fable","onyx","nova","sage","shimmer","verse","marin","cedar"
}
_OPENAI_VOICE_ALIASES = {
    # "Breeze" is a ChatGPT voice name; map it to the closest built-in API voice.
    "breeze": "marin",
    "breezy": "marin",
    "breeze_female": "marin",
}

def _default_voice() -> str:
    return (os.getenv("ETHEREA_TTS_VOICE") or os.getenv("ETHEREA_OPENAI_TTS_VOICE") or "breeze").strip()


def _default_language() -> str:
    return (os.getenv("ETHEREA_TTS_LANG") or "en-IN").strip()


def _build_emotion_instructions(emotion: Optional[str]) -> str:
    # Keep it short and deterministic.
    emotion = (emotion or "").strip().lower()
    if emotion in ("stressed", "anxious"):
        return "Speak calmly, slowly, and reassuringly. Keep a warm, grounded tone."
    if emotion in ("focused", "deep_work"):
        return "Speak crisp and confident, slightly faster. Sound smart and helpful."
    if emotion in ("cheerful", "happy", "excited"):
        return "Speak upbeat, friendly, and energetic. Smile in the voice."
    return "Speak warm, intelligent, and emotionally aware. Sound like a supportive mentor."


@dataclass
class _Job:
    text: str
    language: str
    voice: str
    emotion: str
    backend: str
    options: Dict[str, Any]


class VoiceEngine(QObject):
    """
    Unified voice engine used across the app.

    Design:
      - Single background worker thread.
      - Emits speaking_state + viseme_updated for avatar sync.
      - Chooses best backend automatically (OpenAI -> Edge -> pyttsx3).

    Environment variables:
      - ETHEREA_VOICE_BACKEND = auto|openai|edge|pyttsx3|none
      - ETHEREA_TTS_VOICE = e.g. breeze
      - OPENAI_API_KEY or OPENAI_API_KEY2
    """

    speaking_started = Signal()
    speaking_finished = Signal()
    speaking_state = Signal(bool)
    viseme_updated = Signal(float)
    error = Signal(str)

    _instance: "VoiceEngine | None" = None

    def __init__(self) -> None:
        super().__init__()
        self._q: "queue.Queue[_Job]" = queue.Queue()
        self._stop = threading.Event()
        self._worker = threading.Thread(target=self._loop, daemon=True)
        self._worker.start()

    @classmethod
    def instance(cls) -> "VoiceEngine":
        if cls._instance is None:
            cls._instance = VoiceEngine()
        return cls._instance

    def stop(self) -> None:
        self._stop.set()
        try:
            self._q.put_nowait(_Job("", "", "", "", "none", {}))
        except Exception:
            pass

    def start_wake_word_loop(self) -> None:
        # Placeholder: keep API compatibility; real wake-word is a later phase.
        return

    def speak(self, text: str, **kwargs: Any) -> bool:
        """
        Queue a TTS request (non-blocking).

        Accepted kwargs (safe to ignore if not supported):
          - language: e.g. "en-IN"
          - voice: e.g. "breeze"
          - emotion: e.g. "calm" | "focused" | "cheerful" | "stressed"
          - backend: "auto" | "openai" | "edge" | "pyttsx3" | "none"
          - blocking: bool (if True, speak and wait)
        """
        text = (text or "").strip()
        if not text:
            return False

        language = str(kwargs.get("language") or _default_language())
        voice = str(kwargs.get("voice") or _default_voice())
        emotion = str(kwargs.get("emotion") or kwargs.get("emotion_tag") or "calm")
        backend = _normalize_backend(str(kwargs.get("backend") or os.getenv("ETHEREA_VOICE_BACKEND", "auto")))
        blocking = bool(kwargs.get("blocking", False))

        job = _Job(text=text, language=language, voice=voice, emotion=emotion, backend=backend, options=kwargs)

        if blocking:
            done = threading.Event()
            job.options["_done_event"] = done
            self._q.put(job)
            done.wait()
            return True

        self._q.put(job)
        return True

    # -------------------------
    # internals
    # -------------------------
    def _choose_backend(self, requested: str) -> str:
        if requested in ("openai", "edge", "pyttsx3", "none"):
            return requested

        # auto: OpenAI if key + adapter available
        if _env_key() and callable(speak_openai_tts):
            return "openai"
        if callable(speak_edge_tts):
            return "edge"
        if callable(speak_pyttsx3):
            return "pyttsx3"
        return "none"

    def _emit(self, sig, *args) -> None:  # noqa: ANN001
        try:
            if sig is not None:
                sig.emit(*args)  # type: ignore
        except Exception:
            pass

    def _viseme_pump(self, duration: float, stop_evt: threading.Event) -> None:
        t0 = time.time()
        while not stop_evt.is_set():
            t = time.time() - t0
            if t > duration:
                break
            # pseudo-viseme: lively but not chaotic
            v = 0.18 + 0.55 * abs(__import__("math").sin(t * 9.0))
            self._emit(self.viseme_updated, float(v))
            time.sleep(0.05)
        self._emit(self.viseme_updated, 0.10)

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                job = self._q.get(timeout=0.1)
            except Exception:
                continue

            if self._stop.is_set():
                break

            if not job.text:
                continue

            backend = self._choose_backend(job.backend)

            self._emit(self.speaking_started)
            self._emit(self.speaking_state, True)

            # Animate mouth while speaking
            dur = _estimate_duration(job.text)
            pump_stop = threading.Event()
            pump = threading.Thread(target=self._viseme_pump, args=(dur, pump_stop), daemon=True)
            pump.start()

            ok = False
            try:
                if backend == "openai" and callable(speak_openai_tts):
                    ok = speak_openai_tts(
                        job.text,
                        voice=_OPENAI_VOICE_ALIASES.get(job.voice.lower(), job.voice) if job.voice.lower() not in _OPENAI_VOICES else job.voice,
                        model=os.getenv("ETHEREA_OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
                        instructions=_build_emotion_instructions(job.emotion),
                        fmt=os.getenv("ETHEREA_TTS_FORMAT", "mp3"),
                        speed=float(os.getenv("ETHEREA_TTS_SPEED", "1.0")),
                    )
                elif backend == "edge" and callable(speak_edge_tts):
                    ok = speak_edge_tts(job.text, voice=job.voice, rate="+0%", pitch="+0Hz")  # type: ignore
                elif backend == "pyttsx3" and callable(speak_pyttsx3):
                    ok = speak_pyttsx3(job.text, voice_hint=job.voice, rate=None)  # type: ignore
                else:
                    ok = False
            except Exception as e:
                ok = False
                self._emit(self.error, str(e))

            pump_stop.set()
            try:
                pump.join(timeout=0.5)
            except Exception:
                pass

            self._emit(self.speaking_state, False)
            self._emit(self.speaking_finished)

            done_evt = job.options.get("_done_event")
            if isinstance(done_evt, threading.Event):
                done_evt.set()

            # brief cool-down to prevent stutter
            time.sleep(0.02)


def get_voice_engine() -> VoiceEngine:
    return VoiceEngine.instance()
