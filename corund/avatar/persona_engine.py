from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


def clamp01(x: float) -> float:
    try:
        if x != x:  # NaN
            return 0.5
        return max(0.0, min(1.0, float(x)))
    except Exception:
        return 0.5


@dataclass
class PersonaState:
    emotion_tag: str
    bias: Dict[str, float]


class PersonaEngine:
    """Lightweight, deterministic persona mapping.

    Inputs:
      - mode: study/coding/exam/calm/deep_work/meeting (or anything)
      - tone: gentle_focus/sharp_helpful/strict_calm/etc
      - ei: dict with focus/stress/energy/curiosity in [0..1] preferred

    Output:
      - emotion_tag: stable string used by UI/aurora logs
      - bias: small additive nudges to avatar targets
    """

    def compute(self, *, mode: str, tone: str, ei: Dict[str, Any]) -> Dict[str, Any]:
        mode = (mode or "study").lower()
        tone = (tone or "neutral").lower()

        focus = clamp01(float(ei.get("focus", 0.55)))
        stress = clamp01(float(ei.get("stress", 0.25)))
        energy = clamp01(float(ei.get("energy", 0.65)))
        curiosity = clamp01(float(ei.get("curiosity", 0.55)))

        # --- Base biases by mode (small, safe nudges) ---
        bias = {
            "glow": 0.0,
            "calm": 0.0,
            "motion": 0.0,
            "smile": 0.0,
            "furrow": 0.0,
            "brow_raise": 0.0,
            "gaze_x": 0.0,
            "gaze_y": 0.0,
            "blink_rate": 1.0,
        }

        emotion_tag = "calm"

        if mode in ("exam", "test", "revision"):
            emotion_tag = "strict"
            bias["calm"] += 0.10
            bias["motion"] -= 0.10
            bias["smile"] -= 0.12
            bias["furrow"] += 0.10
            bias["blink_rate"] = 0.85

        elif mode in ("coding", "builder"):
            emotion_tag = "focused"
            bias["glow"] += 0.08
            bias["motion"] += 0.08
            bias["brow_raise"] += 0.08
            bias["blink_rate"] = 1.05

        elif mode in ("deep_work", "focus", "flow"):
            emotion_tag = "flow"
            bias["calm"] += 0.12
            bias["motion"] -= 0.05
            bias["glow"] += 0.05
            bias["blink_rate"] = 0.90

        elif mode in ("meeting",):
            emotion_tag = "professional"
            bias["calm"] += 0.08
            bias["smile"] += 0.02
            bias["motion"] -= 0.05
            bias["blink_rate"] = 1.00

        elif mode in ("calm", "rest", "heal"):
            emotion_tag = "soothing"
            bias["calm"] += 0.18
            bias["motion"] -= 0.12
            bias["smile"] += 0.08
            bias["blink_rate"] = 0.80

        else:  # study/default
            emotion_tag = "gentle_focus"
            bias["calm"] += 0.10
            bias["smile"] += 0.04
            bias["blink_rate"] = 0.95

        # --- Tone overlays (from workspace policy) ---
        if "gentle" in tone:
            emotion_tag = "gentle_focus"
            bias["calm"] += 0.08
            bias["smile"] += 0.05
            bias["motion"] -= 0.03
            bias["blink_rate"] = min(bias["blink_rate"], 0.95)

        if "sharp" in tone or "helpful" in tone:
            emotion_tag = "focused"
            bias["glow"] += 0.06
            bias["brow_raise"] += 0.06

        if "strict" in tone:
            emotion_tag = "strict"
            bias["smile"] -= 0.05
            bias["furrow"] += 0.06
            bias["motion"] -= 0.05

        if "support" in tone or "heal" in tone:
            emotion_tag = "soothing"
            bias["calm"] += 0.10
            bias["smile"] += 0.06

        # --- EI overlays (context-sensitive, still bounded) ---
        # High stress -> soften + reduce motion + add concern brow
        if stress > 0.65:
            emotion_tag = "concerned"
            bias["calm"] += 0.10
            bias["motion"] -= 0.10
            bias["furrow"] += 0.08
            bias["blink_rate"] = max(0.65, bias["blink_rate"] - 0.15)

        # Very high focus -> slight glow, fewer blinks
        if focus > 0.78:
            bias["glow"] += 0.06
            bias["blink_rate"] = min(bias["blink_rate"], 0.90)

        # Low energy -> reduce motion, slightly lower smile
        if energy < 0.35:
            bias["motion"] -= 0.10
            bias["smile"] -= 0.03

        # Curiosity -> micro gaze drift
        bias["gaze_x"] += (curiosity - 0.5) * 0.06
        bias["gaze_y"] += (0.5 - focus) * 0.03

        # Clamp bias magnitudes to keep animation sane
        def cap(k: str, lo: float, hi: float):
            v = float(bias.get(k, 0.0))
            bias[k] = max(lo, min(hi, v))

        cap("glow", -0.25, 0.25)
        cap("calm", -0.25, 0.25)
        cap("motion", -0.30, 0.30)
        cap("smile", -0.25, 0.25)
        cap("furrow", -0.25, 0.25)
        cap("brow_raise", -0.25, 0.25)
        cap("gaze_x", -0.20, 0.20)
        cap("gaze_y", -0.20, 0.20)
        cap("blink_rate", 0.40, 2.50)

        return {"emotion_tag": emotion_tag, "bias": bias}
