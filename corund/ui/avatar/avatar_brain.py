from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import QPointF, QRectF


@dataclass
class BrainState:
    mood: str = "calm"
    last_interaction: float = 0.0
    last_surprise: float = 0.0
    last_quip: str = ""


class AvatarBrain:
    def __init__(self) -> None:
        self.state = BrainState()
        self._wander_target: Optional[QPointF] = None
        self._wander_until = 0.0
        self.dramatic_mode = False

    def update(self, bounds: QRectF, now: float) -> Optional[QPointF]:
        if now > self._wander_until or self._wander_target is None:
            self._wander_target = QPointF(
                random.uniform(bounds.left() + 20, bounds.right() - 20),
                random.uniform(bounds.top() + 20, bounds.bottom() - 20),
            )
            self._wander_until = now + random.uniform(2.5, 5.0)
        return self._wander_target

    def on_hover(self) -> str:
        self.state.last_interaction = time.time()
        self.state.mood = "focus"
        return self._quip(
            "I’m right here if you want a focus boost.",
            "A spotlight moment! Need a quick plan?",
        )

    def on_click(self) -> str:
        self.state.last_interaction = time.time()
        self.state.mood = "excited"
        return self._quip(
            "Sparkle time! Want me to open a workspace?",
            "Cue the confetti—what’s our next move?",
        )

    def on_idle(self) -> str:
        self.state.mood = "calm"
        return self._quip(
            "I can stay quiet, or share a gentle check-in.",
            "Want a calm reset or a tiny task list?",
        )

    def on_task_complete(self) -> str:
        self.state.mood = "calm"
        return self._quip(
            "Nice finish! Want a breather or another quest?",
            "Mission cleared. Ready for the next one?",
        )

    def _quip(self, base: str, dramatic: str) -> str:
        line = dramatic if self.dramatic_mode else base
        self.state.last_quip = line
        return line
