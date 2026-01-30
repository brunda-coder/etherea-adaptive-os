from typing import Dict, Any
import math


class EmotionMapper:
    """
    Translates an EmotionVector (focus, stress, energy, curiosity)
    into visual parameters for a 3D avatar. Uses smooth easing (lerp)
    with optional delta-time scaling so responsiveness is frame-rate
    independent.
    """

    def __init__(self, lerp_factor: float = 0.05):
        # Current eased values
        self.params: Dict[str, float] = {
            "eye_openness": 0.5,
            "blink_rate": 0.1,
            "gaze_jitter": 0.0,
            "breathing_intensity": 0.5,
            "glow_intensity": 0.5,
            "color_temp": 0.5,
            "pulse_speed": 0.5,
            "particle_density": 0.5,
        }

        # Targets we lerp toward
        self.target_params: Dict[str, float] = self.params.copy()

        # Base responsiveness (per-frame equivalent). Smaller -> slower.
        self.lerp_factor = float(max(0.0, min(1.0, lerp_factor)))

    def update(self, emotion_vector: Dict[str, Any], dt: float = 0.016) -> Dict[str, float]:
        try:
            focus = float(emotion_vector.get("focus", 0.5))
        except Exception:
            focus = 0.5
        try:
            stress = float(emotion_vector.get("stress", 0.2))
        except Exception:
            stress = 0.2
        try:
            energy = float(emotion_vector.get("energy", 0.5))
        except Exception:
            energy = 0.5
        try:
            curiosity = float(emotion_vector.get("curiosity", 0.5))
        except Exception:
            curiosity = 0.5

        focus = self._clamp(focus)
        stress = self._clamp(stress)
        energy = self._clamp(energy)
        curiosity = self._clamp(curiosity)

        self.target_params["eye_openness"] = 0.4 + (focus * 0.4)
        self.target_params["blink_rate"] = 0.05 + (stress * 0.2)
        self.target_params["gaze_jitter"] = stress * 0.3
        self.target_params["pulse_speed"] = 0.2 + (stress * 0.8)
        self.target_params["breathing_intensity"] = 0.3 + (energy * 0.7)
        self.target_params["glow_intensity"] = 0.3 + (0.6 * focus) + (0.1 * curiosity) - (0.25 * stress)
        self.target_params["color_temp"] = 0.3 + (0.4 * focus) + (0.3 * energy) - (0.3 * stress)
        self.target_params["particle_density"] = 0.2 + (0.6 * curiosity) + (0.2 * energy)

        alpha = self._alpha(dt)
        for key, target in self.target_params.items():
            target = self._clamp(target)
            current = self.params.get(key, 0.5)
            self.params[key] = self._clamp(self._lerp(current, target, alpha))

        return self.params.copy()

    def _alpha(self, dt: float) -> float:
        if dt is None:
            return self.lerp_factor
        try:
            dt = float(dt)
        except Exception:
            return self.lerp_factor
        if dt <= 0:
            return 0.0
        scale = dt / 0.016
        return min(1.0, self.lerp_factor * scale)

    def _lerp(self, a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    def _clamp(self, value: float) -> float:
        try:
            if math.isnan(value) or math.isinf(value):
                return 0.5
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.5


mapper = EmotionMapper()
