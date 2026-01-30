from __future__ import annotations

import math
from typing import Dict

from corund.ui.avatar_engine.registry import AVATARS, AvatarSpec


def _clamp01(x: float) -> float:
    try:
        if math.isnan(x) or math.isinf(x):
            return 0.5
        return max(0.0, min(1.0, float(x)))
    except Exception:
        return 0.5


class AvatarEngine:
    """
    Keeps the avatar state: selected avatar, EI vector, and animation parameters.
    Pure logic (no UI) so it's stable and testable.
    """

    def __init__(self):
        self.avatar: AvatarSpec = AVATARS["aurora"]

        # Emotion vector from EIEngine
        self.ei: Dict[str, float] = {
            "focus": 0.5,
            "stress": 0.2,
            "energy": 0.6,
            "curiosity": 0.5,
        }

        # Visual state derived from EI
        self.glow_intensity: float = 0.7
        self.motion_multiplier: float = 1.0

        # smooth transitions
        self._target_key = self.avatar.key
        self._blend = 1.0  # 0..1
        self._blend_speed = 3.0

    def set_avatar(self, key: str):
        if key in AVATARS:
            self._target_key = key
            self._blend = 0.0

    def update_ei(self, vec: Dict[str, float]):
        for k in self.ei:
            if k in vec:
                self.ei[k] = _clamp01(vec[k])

        # Map EI → visuals
        focus = self.ei["focus"]
        stress = self.ei["stress"]
        energy = self.ei["energy"]
        curiosity = self.ei["curiosity"]

        # Glow stronger when focused/curious, but unstable when stressed
        base = 0.35 + 0.55 * focus + 0.25 * curiosity
        penalty = 0.30 * stress
        self.glow_intensity = _clamp01(base - penalty)

        # Motion increases with energy, decreases with stress
        self.motion_multiplier = _clamp01(0.55 + 0.85 * energy - 0.40 * stress)

    def tick(self, dt: float) -> float:
        """
        dt = seconds since last frame
        returns blend value 0..1 (useful for UI transitions)
        """
        # handle crossfade to new avatar
        if self._target_key != self.avatar.key:
            self._blend = min(1.0, self._blend + dt * self._blend_speed)
            if self._blend >= 1.0:
                self.avatar = AVATARS[self._target_key]
                self._blend = 1.0
        return self._blend
