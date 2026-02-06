from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AuroraState:
    """Visual Aurora state for rendering."""

    intensity: float = 0.5
    pulse_speed: float = 1.0
    temperature: float = 0.2
    mood: str = "neutral"


@dataclass
class AuroraRuntimeState:
    current_mode: str = "idle"
    dnd_active: bool = False
    workspace_id: str | None = None
    workspace_name: str | None = None
    session_active: bool = False
    last_saved: str | None = None


class AuroraStateStore:
    """Simple mutable store consumed by AuroraDecisionPipeline."""

    def __init__(self, _registry=None) -> None:
        self.visual = AuroraState()
        self.runtime = AuroraRuntimeState()

    def update(self, **kwargs) -> AuroraRuntimeState:
        for key, value in kwargs.items():
            if hasattr(self.runtime, key):
                setattr(self.runtime, key, value)
        return self.runtime


_aurora_state_instance = AuroraState()


def get_aurora_state() -> AuroraState:
    return _aurora_state_instance


def update_aurora_state(
    intensity: float = None,
    pulse_speed: float = None,
    temperature: float = None,
    mood: str = None,
):
    global _aurora_state_instance

    if intensity is not None:
        _aurora_state_instance.intensity = max(0.0, min(1.0, intensity))
    if pulse_speed is not None:
        _aurora_state_instance.pulse_speed = max(0.5, min(2.0, pulse_speed))
    if temperature is not None:
        _aurora_state_instance.temperature = max(0.0, min(1.0, temperature))
    if mood is not None:
        _aurora_state_instance.mood = mood
