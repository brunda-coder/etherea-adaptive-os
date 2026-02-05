from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CameraInference:
    probabilities: dict
    confidence: float


class CameraInferer:
    def __init__(self) -> None:
        self.enabled = False

    def infer(self) -> CameraInference:
        if not self.enabled:
            return CameraInference(probabilities={}, confidence=0.0)
        # Stub: local-only camera inference would run here.
        return CameraInference(probabilities={"calm": 0.4, "focused": 0.3}, confidence=0.2)
