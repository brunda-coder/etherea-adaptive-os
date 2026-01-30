from __future__ import annotations
from typing import List, Dict, Any, Optional

from PySide6.QtCore import QObject, QTimer


class BeatSyncScheduler(QObject):
    """
    Schedules UI effects (ring pulses/highlights) using a QTimer.
    Works only in desktop builds with PySide6.
    """

    def __init__(self, apply_effect_cb, log_cb=None):
        super().__init__()
        self.apply_effect_cb = apply_effect_cb
        self.log_cb = log_cb or (lambda *a, **k: None)

        self._timeline: List[Dict[str, Any]] = []
        self._idx = 0
        self._start_ms = 0

        self._timer = QTimer()
        self._timer.setInterval(16)  # ~60fps tick
        self._timer.timeout.connect(self._tick)

    def load(self, ui_effects: List[Dict[str, Any]]):
        # Sort by time
        self._timeline = sorted(ui_effects or [], key=lambda x: float(x.get("t", 0.0)))
        self._idx = 0

    def start(self):
        if not self._timeline:
            self.log_cb("⚠️ BeatSync: No effects to schedule")
            return

        self._start_ms = 0
        self._idx = 0
        self._timer.start()
        self.log_cb(f"💫 BeatSync: started ({len(self._timeline)} effects)")

    def stop(self):
        self._timer.stop()
        self._timeline = []
        self._idx = 0
        self._start_ms = 0
        self.log_cb("💫 BeatSync: stopped")

    def _tick(self):
        # Lazy init start time on first tick
        if self._start_ms == 0:
            self._start_ms = self._now_ms()

        elapsed_s = (self._now_ms() - self._start_ms) / 1000.0

        # Fire all effects whose time <= elapsed
        while self._idx < len(self._timeline):
            e = self._timeline[self._idx]
            t = float(e.get("t", 0.0))
            if t > elapsed_s:
                break

            try:
                self.apply_effect_cb(e)
            except Exception as ex:
                self.log_cb(f"⚠️ BeatSync apply_effect failed: {ex}")

            self._idx += 1

        # Auto-stop when done
        if self._idx >= len(self._timeline):
            self.stop()

    def _now_ms(self) -> int:
        # QTimer doesn't expose now; use python time
        import time
        return int(time.time() * 1000)
