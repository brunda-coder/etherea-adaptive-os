from __future__ import annotations
from typing import List, Dict, Any


def beats_to_ui_effects(beats, base_intensity: float = 1.15, downbeat_intensity: float = 1.55) -> List[Dict[str, Any]]:
    """
    Convert beat list -> Aurora ring pulse UI effects timeline.
    beats: list of objects with .t and .strength
    """
    effects: List[Dict[str, Any]] = []
    for b in beats:
        effects.append({
            "t": float(getattr(b, "t", 0.0)),
            "type": "ring_pulse",
            "dur": 0.18,
            "intensity": downbeat_intensity if float(getattr(b, "strength", 0.5)) >= 0.9 else base_intensity
        })
    return effects
