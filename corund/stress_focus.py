from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StressFocusState:
    stress: float
    focus: float
    confidence: float
    source: str = "keyboard_mouse"


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def compute_stress_focus(metrics: dict) -> StressFocusState:
    """Stable heuristic API for stress/focus from keyboard + mouse dynamics."""
    keyboard = metrics.get("keyboard") or {}
    mouse = metrics.get("mouse") or {}

    key_rate = float(keyboard.get("press_rate", keyboard.get("intensity", 0.0)))
    key_burst = float(keyboard.get("burstiness", keyboard.get("variance", 0.0)))
    mouse_move = float(mouse.get("move_rate", mouse.get("intensity", 0.0)))
    mouse_clicks = float(mouse.get("click_rate", mouse.get("clicks", 0.0)))
    mouse_jitter = float(mouse.get("jitter", 0.0))

    focus = _clamp((0.58 * key_rate) + (0.22 * mouse_move) - (0.20 * key_burst))
    stress = _clamp((0.50 * mouse_jitter) + (0.22 * mouse_clicks) + (0.18 * key_burst) - (0.15 * key_rate))
    confidence = _clamp(0.6 + 0.2 * min(1.0, key_rate + mouse_move) + 0.2 * min(1.0, mouse_clicks + key_burst))
    return StressFocusState(stress=stress, focus=focus, confidence=confidence)

