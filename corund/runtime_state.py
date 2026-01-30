from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MetricValue:
    value: float
    source: str
    timestamp: str


@dataclass
class AudioState:
    bg_audio_active: bool = False
    tts_active: bool = False


@dataclass
class OverridesState:
    kill_switch: bool = False
    dnd: bool = False
    manual_lock: bool = False
    privacy_mode: bool = False


@dataclass
class WorkspaceState:
    workspace_id: Optional[str] = None
    workspace_name: Optional[str] = None
    session_active: bool = False
    last_saved: Optional[str] = None
    session_info: Dict[str, object] = field(default_factory=dict)


@dataclass
class VisualSettings:
    reduce_motion: bool = False
    intensity_preset: str = "normal"


@dataclass
class RuntimeState:
    focus: MetricValue = field(default_factory=lambda: MetricValue(0.5, "init", now_iso()))
    stress: MetricValue = field(default_factory=lambda: MetricValue(0.2, "init", now_iso()))
    energy: MetricValue = field(default_factory=lambda: MetricValue(0.6, "init", now_iso()))
    current_mode: str = "idle"
    last_intent: Optional[str] = None
    avatar_state: str = "idle"
    emotion_tag: str = "calm"
    intensity: float = 0.5
    audio_state: AudioState = field(default_factory=AudioState)
    overrides: OverridesState = field(default_factory=OverridesState)
    workspace_state: WorkspaceState = field(default_factory=WorkspaceState)
    visual_settings: VisualSettings = field(default_factory=VisualSettings)
    language_code: str = "en-IN"

    def update_metric(self, key: str, value: float, source: str) -> None:
        metric = MetricValue(value=value, source=source, timestamp=now_iso())
        if key == "focus":
            self.focus = metric
        elif key == "stress":
            self.stress = metric
        elif key == "energy":
            self.energy = metric
