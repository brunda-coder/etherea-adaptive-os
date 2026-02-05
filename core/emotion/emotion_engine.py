from __future__ import annotations

import time
from dataclasses import dataclass

from core.emotion.camera_infer import CameraInferer
from core.emotion.privacy import EmotionPrivacyManager
from core.emotion.signals import EmotionSignals, _clamp


@dataclass
class UserState:
    probabilities: dict
    confidence: float


class EmotionEngine:
    def __init__(self) -> None:
        self.signals = EmotionSignals()
        self.privacy = EmotionPrivacyManager()
        self.camera_inferer = CameraInferer()
        self.enabled = True
        self._last_tick = time.time()
        self.user_state = UserState(probabilities={}, confidence=0.0)

        try:
            from corund.signals import signals

            signals.input_activity.connect(self._on_input_activity)
        except Exception:
            pass

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def set_camera_opt_in(self, enabled: bool) -> None:
        self.camera_inferer.enabled = enabled
        self.privacy.set_camera_opt_in(enabled)

    def set_kill_switch(self, enabled: bool) -> None:
        self.privacy.set_kill_switch(enabled)

    def delete_data(self) -> None:
        self.signals = EmotionSignals()
        self.privacy.delete_data()
        self.user_state = UserState(probabilities={}, confidence=0.0)

    def record_typing(self, intensity: float, variance: float) -> None:
        self.signals.update_typing(intensity, variance)

    def record_app_switch(self, rate: float) -> None:
        self.signals.update_app_switch(rate)

    def record_idle_jitter(self, jitter: float) -> None:
        self.signals.update_idle_jitter(jitter)

    def record_error(self, rate: float) -> None:
        self.signals.update_error_rate(rate)

    def record_voice_sentiment(self, score: float) -> None:
        # Stub for future voice sentiment fusion.
        self.signals.update_error_rate(max(0.0, 0.1 - score))

    def _on_input_activity(self, activity_type: str, payload) -> None:
        if not isinstance(payload, dict):
            payload = {"intensity": payload}
        intensity = float(payload.get("intensity", 0.0))
        variance = float(payload.get("variance", 0.5))
        jitter = float(payload.get("jitter", 0.0))

        if activity_type == "typing":
            self.record_typing(intensity, variance)
        elif activity_type == "mouse":
            self.record_idle_jitter(jitter)

    def tick(self) -> UserState:
        now = time.time()
        dt = max(0.0, min(1.0, now - self._last_tick))
        self._last_tick = now

        if not self.enabled or self.privacy.state.kill_switch:
            self.user_state = UserState(probabilities={"neutral": 1.0}, confidence=0.0)
            return self.user_state

        self.signals.decay(amount=0.02 * dt)

        base_confidence = _clamp(
            (self.signals.typing_speed + self.signals.app_switch_rate + self.signals.idle_jitter + self.signals.error_rate) / 4.0
        )

        focus = _clamp(self.signals.typing_speed * 0.6 + (1.0 - self.signals.app_switch_rate) * 0.2)
        frustrated = _clamp(self.signals.error_rate * 0.6 + self.signals.idle_jitter * 0.4 + self.signals.app_switch_rate * 0.2)
        calm = _clamp(1.0 - frustrated * 0.7 - self.signals.app_switch_rate * 0.2)
        tired = _clamp(self.signals.idle_jitter * 0.6 + (1.0 - self.signals.typing_speed) * 0.3)
        excited = _clamp(self.signals.typing_speed * 0.4 + self.signals.app_switch_rate * 0.2)

        probabilities = {
            "calm": calm,
            "focused": focus,
            "frustrated": frustrated,
            "tired": tired,
            "excited": excited,
        }

        camera = self.camera_inferer.infer() if self.camera_inferer.enabled else None
        if camera and camera.confidence > 0:
            for key, value in camera.probabilities.items():
                probabilities[key] = _clamp(probabilities.get(key, 0.0) + value * 0.3)
            base_confidence = _clamp((base_confidence + camera.confidence) / 2.0)

        self.user_state = UserState(probabilities=probabilities, confidence=base_confidence)
        return self.user_state


_emotion_engine: EmotionEngine | None = None


def get_emotion_engine() -> EmotionEngine:
    global _emotion_engine
    if _emotion_engine is None:
        _emotion_engine = EmotionEngine()
    return _emotion_engine
