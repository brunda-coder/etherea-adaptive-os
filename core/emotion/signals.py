from __future__ import annotations

from dataclasses import dataclass


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


@dataclass
class EmotionSignals:
    typing_speed: float = 0.0
    app_switch_rate: float = 0.0
    idle_jitter: float = 0.0
    error_rate: float = 0.0

    def decay(self, amount: float = 0.03) -> None:
        self.typing_speed = _clamp(self.typing_speed - amount)
        self.app_switch_rate = _clamp(self.app_switch_rate - amount * 0.8)
        self.idle_jitter = _clamp(self.idle_jitter - amount * 0.5)
        self.error_rate = _clamp(self.error_rate - amount * 0.7)

    def update_typing(self, intensity: float, variance: float) -> None:
        self.typing_speed = _clamp(self.typing_speed + intensity * 0.6 + (1.0 - variance) * 0.2)

    def update_app_switch(self, rate: float) -> None:
        self.app_switch_rate = _clamp(self.app_switch_rate + rate * 0.5)

    def update_idle_jitter(self, jitter: float) -> None:
        self.idle_jitter = _clamp(max(self.idle_jitter, jitter))

    def update_error_rate(self, rate: float) -> None:
        self.error_rate = _clamp(self.error_rate + rate * 0.4)
