from __future__ import annotations

import importlib
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class RuntimeCapabilities:
    voice_available: bool
    camera_available: bool
    pygame_available: bool

    def to_dict(self) -> dict[str, bool]:
        return asdict(self)


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


def detect_capabilities() -> RuntimeCapabilities:
    voice_available = any(
        _module_available(mod)
        for mod in ("openai", "edge_tts", "pyttsx3")
    )
    camera_available = _module_available("cv2")
    pygame_available = _module_available("pygame")
    return RuntimeCapabilities(
        voice_available=voice_available,
        camera_available=camera_available,
        pygame_available=pygame_available,
    )
