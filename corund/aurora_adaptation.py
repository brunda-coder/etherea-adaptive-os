from __future__ import annotations

from dataclasses import dataclass

from corund.stress_focus import StressFocusState, compute_stress_focus


@dataclass(frozen=True)
class AuroraRecommendation:
    color: str
    intensity: float
    visible: bool
    mood: str


class AuroraAdaptationEngine:
    """Stable adaptation API for Aurora ring state."""

    def recommend(
        self,
        *,
        hour: int,
        metrics: dict,
        tutorial_active: bool = False,
        face_mood: str | None = None,
        mic_mood: str | None = None,
    ) -> AuroraRecommendation:
        sf: StressFocusState = compute_stress_focus(metrics)
        mood = (face_mood or mic_mood or "neutral").lower()

        color = "calm"
        if sf.stress >= 0.75:
            color = "stress"
        elif sf.focus >= 0.65:
            color = "focus"
        elif hour < 6 or hour >= 22:
            color = "idle"

        if mood in {"angry", "stressed", "anxious"}:
            color = "stress"

        intensity = max(0.15, min(1.0, 0.35 + 0.5 * sf.focus + 0.3 * sf.stress))
        visible = not tutorial_active
        return AuroraRecommendation(color=color, intensity=intensity, visible=visible, mood=mood)
