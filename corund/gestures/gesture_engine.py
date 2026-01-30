from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from PySide6.QtCore import QObject, QTimer
except Exception:
    QObject = object  # type: ignore
    QTimer = None     # type: ignore


class GestureEngine(QObject):
    """
    Safe gesture timeline runner.
    - Works when PySide6 is present (desktop builds)
    - Does nothing (but doesn't crash) when PySide6 is missing (Termux)
    """

    def __init__(self, avatar_widget=None, on_log=None):
        super().__init__()
        self.avatar = avatar_widget
        self.on_log = on_log
        self._timers: List[Any] = []

    def log(self, msg: str):
        if self.on_log:
            try:
                self.on_log(msg)
                return
            except Exception:
                pass
        # fallback
        print(msg)

    def stop(self):
        # cancel pending timers
        for t in self._timers:
            try:
                t.stop()
                t.deleteLater()
            except Exception:
                pass
        self._timers.clear()

    def play(self, plan: Dict[str, Any]):
        """
        plan = {
          "gestures":[{"t":0.2,"type":"nod","dur":0.6}, ...],
          "ui_effects":[{"t":1.2,"type":"ring_highlight","segment":3,"dur":1.0}, ...]
        }
        """
        self.stop()

        if QTimer is None:
            self.log("⚠️ GestureEngine: PySide6 not available here (Termux). Skipping animations safely.")
            return

        gestures = plan.get("gestures", [])
        effects = plan.get("ui_effects", [])

        def schedule(item: Dict[str, Any], kind: str):
            t_sec = float(item.get("t", 0.0))
            ms = max(0, int(t_sec * 1000))

            timer = QTimer(self)
            timer.setSingleShot(True)

            def fire():
                try:
                    self._fire_item(item, kind)
                except Exception as e:
                    self.log(f"⚠️ GestureEngine error ({kind}): {e}")

            timer.timeout.connect(fire)
            timer.start(ms)
            self._timers.append(timer)

        for g in gestures:
            schedule(g, "gesture")
        for e in effects:
            schedule(e, "effect")

        self.log("🎬 Gesture timeline started.")

    def _fire_item(self, item: Dict[str, Any], kind: str):
        if not self.avatar:
            self.log("⚠️ GestureEngine: no avatar widget attached.")
            return

        name = str(item.get("type", "")).strip()
        dur = float(item.get("dur", 0.8))
        intensity = float(item.get("intensity", 1.0))

        # gestures
        if kind == "gesture":
            if hasattr(self.avatar, "perform_gesture"):
                self.avatar.perform_gesture(name, dur=dur, intensity=intensity)
                self.log(f"🤖 gesture: {name} ({dur}s)")
                return
            self.log("⚠️ Avatar missing perform_gesture().")

        # UI effects (ring highlight etc.)
        if kind == "effect":
            if name == "ring_highlight" and hasattr(self.avatar, "ring_highlight"):
                seg = int(item.get("segment", 0))
                self.avatar.ring_highlight(seg, dur=dur)
                self.log(f"💫 ring_highlight seg={seg} ({dur}s)")
                return

            if name == "ring_pulse" and hasattr(self.avatar, "ring_pulse"):
                self.avatar.ring_pulse(dur=dur, intensity=intensity)
                self.log(f"✨ ring_pulse ({dur}s)")
                return

            self.log(f"⚠️ Unknown effect or missing handler: {name}")
