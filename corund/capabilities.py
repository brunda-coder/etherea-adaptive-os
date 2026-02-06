from __future__ import annotations

import importlib
import importlib.util
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
        try:
            importlib.import_module(name)
            return True
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



def selftest_detect_capabilities_guard() -> tuple[bool, str]:
    """
    Sanity-check that detect_capabilities() tolerates importlib util lookup failures
    and still reports available modules when fallback import succeeds.
    """
    original_find_spec = importlib.util.find_spec

    def _raising_find_spec(_name: str):
        raise AttributeError("simulated util failure")

    def _fallback_module_available(name: str) -> bool:
        try:
            __import__(name)
            return True
        except Exception:
            return False

    try:
        importlib.util.find_spec = _raising_find_spec
        baseline = detect_capabilities().to_dict()
        fallback = {
            "voice_available": any(_fallback_module_available(mod) for mod in ("openai", "edge_tts", "pyttsx3")),
            "camera_available": _fallback_module_available("cv2"),
            "pygame_available": _fallback_module_available("pygame"),
        }
        under_reports = any(fallback[k] and not baseline[k] for k in fallback)
        if under_reports:
            return False, f"under-reported baseline={baseline} fallback={fallback}"
        return True, f"baseline={baseline} fallback={fallback}"
    finally:
        importlib.util.find_spec = original_find_spec
