from __future__ import annotations
from typing import Any, Dict


def plan_behavior(user_text: str, language: str = "en", emotion: str = "calm") -> Dict[str, Any]:
    """
    Convert user intent -> performance plan:
    - gestures timeline
    - ring effects
    - voice settings
    - emotion target
    - motion clip
    - dance routine parameters (optional)
    """
    text_raw = user_text or ""
    text = text_raw.lower()

    # Simple intent detection
    is_explain = any(k in text for k in ["explain", "what is", "define", "tell me about", "regression", "derivation"])
    is_math = any(k in text for k in ["regression", "centroid", "matrix", "integration", "differential", "probability"])
    is_fast = any(k in text for k in ["quick", "fast", "short"])
    is_dance = any(k in text for k in ["dance", "hype", "party", "vibe"])
    is_sing  = any(k in text for k in ["sing", "song", "music mode"])

    # Voice plan
    voice = {
        "language": language,
        "rate": 1.0 if not is_fast else 1.15,
        "style": "teacher" if is_explain else "neutral",
    }

    # Emotion target
    emotion_target = emotion
    if any(k in text for k in ["stress", "panic", "anxious", "scared"]):
        emotion_target = "reassuring"
    if any(k in text for k in ["angry", "hate", "annoyed"]):
        emotion_target = "calm_confident"

    # Gestures + ring FX (micro-performance)
    gestures = [
        {"t": 0.2, "type": "idle_breathe", "dur": 1.2},
        {"t": 0.7, "type": "hand_raise", "dur": 0.9},
    ]
    ui_effects = [{"t": 0.9, "type": "ring_pulse", "dur": 1.0, "intensity": 1.1}]

    if is_explain:
        gestures += [
            {"t": 1.4, "type": "point_right", "dur": 1.0},
            {"t": 2.6, "type": "nod", "dur": 0.7},
        ]
        ui_effects += [
            {"t": 1.4, "type": "ring_highlight", "segment": 3 if is_math else 1, "dur": 1.1},
            {"t": 2.4, "type": "ring_highlight", "segment": 6 if is_math else 4, "dur": 1.0},
        ]

    # Motion selection (Phase-1 stub)
    motion = {"clip": "idle_breathe_01", "intensity": 1.0, "loop": True}

    if is_dance:
        motion = {"clip": "dance_hype_01", "intensity": 1.25, "loop": True}
    elif is_sing:
        motion = {"clip": "sing_soft_loop", "intensity": 1.05, "loop": True}
    elif is_explain:
        motion = {"clip": "explain_loop_01", "intensity": 1.0, "loop": True}
    elif emotion_target in ("reassuring", "calm"):
        motion = {"clip": "idle_breathe_01", "intensity": 0.9, "loop": True}

    # Dance plan (NEW)
    dance = None
    if is_dance:
        # default dance parameters (later: beat detect from song)
        dance = {"duration_s": 18.0, "bpm": 128.0, "style": "bolly_pop"}

        # Add beat-synced UI pulses (no audio analysis yet)
        try:
            from corund.avatar_motion.dance_planner import generate_beat_grid
            beats = generate_beat_grid(duration_s=dance["duration_s"], bpm=dance["bpm"])
            for b in beats:
                ui_effects.append({
                    "t": b.t,
                    "type": "ring_pulse",
                    "dur": 0.18,
                    "intensity": 1.55 if b.strength >= 0.9 else 1.15
                })
        except Exception:
            pass

    return {
        "voice": voice,
        "emotion_target": emotion_target,
        "gestures": gestures,
        "ui_effects": ui_effects,
        "motion": motion,
        "dance": dance,
    }
