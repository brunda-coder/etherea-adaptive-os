from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from corund.runtime_state import RuntimeState


@dataclass(frozen=True)
class VisualState:
    glow_level: float
    pulse_speed: float
    breath_rate: float
    eye_blink_rate: float
    idle_sway_amp: float
    speaking_bob_amp: float
    thinking_orbit_speed: float
    blocked_dim_level: float
    error_flicker: bool
    caption_style: str


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


STATE_BASE: Dict[str, Dict[str, float]] = {
    "idle": {"pulse": 0.9, "breath": 0.8, "sway": 0.3, "bob": 0.05, "orbit": 0.3},
    "listening": {"pulse": 1.1, "breath": 0.9, "sway": 0.25, "bob": 0.1, "orbit": 0.35},
    "thinking": {"pulse": 1.0, "breath": 0.85, "sway": 0.2, "bob": 0.08, "orbit": 0.65},
    "speaking": {"pulse": 1.5, "breath": 1.0, "sway": 0.25, "bob": 0.35, "orbit": 0.4},
    "blocked": {"pulse": 0.4, "breath": 0.7, "sway": 0.05, "bob": 0.05, "orbit": 0.1},
    "error": {"pulse": 1.1, "breath": 0.75, "sway": 0.15, "bob": 0.15, "orbit": 0.35},
    "muted": {"pulse": 0.6, "breath": 0.8, "sway": 0.2, "bob": 0.05, "orbit": 0.2},
}


EMOTION_TONE: Dict[str, Dict[str, float]] = {
    "bright": {"glow": 0.2, "pulse": 0.15},
    "proud": {"glow": 0.15, "pulse": 0.1},
    "apologetic": {"glow": -0.2, "pulse": -0.1},
    "concerned": {"glow": -0.15, "pulse": -0.08},
    "curious": {"blink": 0.2, "orbit": 0.1},
    "steady": {"sway": -0.1},
    "serious": {"sway": -0.12, "pulse": -0.05},
}


def compute_visual_state(runtime: RuntimeState) -> VisualState:
    avatar_state = runtime.avatar_state or "idle"
    base = STATE_BASE.get(avatar_state, STATE_BASE["idle"])
    intensity = clamp(runtime.intensity, 0.1, 1.0)
    tone = EMOTION_TONE.get(runtime.emotion_tag, {})

    glow = clamp(0.6 + tone.get("glow", 0.0) + (intensity - 0.5) * 0.3, 0.2, 1.0)
    pulse = clamp(base["pulse"] + tone.get("pulse", 0.0), 0.4, 2.2)
    breath = clamp(base["breath"], 0.5, 1.4)
    blink = clamp(0.6 + tone.get("blink", 0.0), 0.4, 1.4)
    sway = clamp(base["sway"] + tone.get("sway", 0.0), 0.0, 0.6)
    bob = clamp(base["bob"], 0.0, 0.5)
    orbit = clamp(base["orbit"] + tone.get("orbit", 0.0), 0.1, 1.2)

    if runtime.overrides.dnd or runtime.overrides.kill_switch:
        blocked_dim = 0.6
    else:
        blocked_dim = 0.0

    error_flicker = avatar_state == "error"
    caption_style = "alert" if avatar_state in {"error", "blocked"} else "calm"

    if runtime.visual_settings.reduce_motion:
        sway = min(sway, 0.1)
        bob = min(bob, 0.15)
        orbit = min(orbit, 0.3)

    return VisualState(
        glow_level=glow,
        pulse_speed=pulse * (0.7 + intensity * 0.6),
        breath_rate=breath,
        eye_blink_rate=blink,
        idle_sway_amp=sway,
        speaking_bob_amp=bob * intensity,
        thinking_orbit_speed=orbit,
        blocked_dim_level=blocked_dim,
        error_flicker=error_flicker,
        caption_style=caption_style,
    )
