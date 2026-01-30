from __future__ import annotations

from typing import Any, Dict


def regression_preset() -> Dict[str, Any]:
    """
    Cinematic micro-gestures + ring effects timed like an explainer.
    """
    return {
        "gestures": [
            {"t": 0.2, "type": "idle_breathe", "dur": 1.2},
            {"t": 0.6, "type": "hand_raise", "dur": 0.8},
            {"t": 1.2, "type": "point_right", "dur": 1.0},
            {"t": 2.4, "type": "nod", "dur": 0.7},
            {"t": 3.2, "type": "smile", "dur": 1.0},
        ],
        "ui_effects": [
            {"t": 1.2, "type": "ring_highlight", "segment": 3, "dur": 1.1},
            {"t": 2.0, "type": "ring_pulse", "dur": 1.0, "intensity": 1.2},
            {"t": 3.0, "type": "ring_highlight", "segment": 6, "dur": 1.0},
        ],
    }
