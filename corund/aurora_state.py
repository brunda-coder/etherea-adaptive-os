from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional

from corund.aurora_actions import ActionRegistry, ActionSpec


@dataclass(frozen=True)
class ActionItem:
    action_id: str
    label: str
    intent: str
    enabled: bool


@dataclass(frozen=True)
class AuroraCanvasState:
    current_mode: str
    focus: float
    stress: float
    energy: float
    workspace_id: Optional[str]
    workspace_name: Optional[str]
    session_active: bool
    layout_density: str
    attention_level: str
    suggested_actions: List[ActionItem]
    theme_profile: Dict[str, str | bool]
    nonessential_opacity: float
    spacing: int
    panel_visibility: Dict[str, bool]
    overlay_text: str
    warning_text: str
    last_saved: Optional[str]


@dataclass
class AuroraRuntimeState:
    current_mode: str = "idle"
    focus: float = 0.4
    stress: float = 0.2
    energy: float = 0.6
    workspace_id: Optional[str] = None
    workspace_name: Optional[str] = None
    session_active: bool = False
    reduce_motion: bool = False
    emotion_tag: str = "calm"
    dnd_active: bool = False
    error_active: bool = False
    last_saved: Optional[str] = None


@dataclass(frozen=True)
class ModeRule:
    layout_density: str
    nonessential_opacity: float
    spacing: int
    panel_visibility: Dict[str, bool]
    overlay_text: str
    warning_text: str


MODE_RULES: Dict[str, ModeRule] = {
    "idle": ModeRule(
        layout_density="calm",
        nonessential_opacity=0.85,
        spacing=12,
        panel_visibility={"actions": True, "status": True, "session": True},
        overlay_text="",
        warning_text="",
    ),
    "focus": ModeRule(
        layout_density="dense",
        nonessential_opacity=0.35,
        spacing=6,
        panel_visibility={"actions": True, "status": True, "session": True},
        overlay_text="",
        warning_text="",
    ),
    "break": ModeRule(
        layout_density="calm",
        nonessential_opacity=0.75,
        spacing=14,
        panel_visibility={"actions": True, "status": True, "session": True},
        overlay_text="",
        warning_text="",
    ),
    "blocked": ModeRule(
        layout_density="calm",
        nonessential_opacity=0.2,
        spacing=8,
        panel_visibility={"actions": True, "status": True, "session": True},
        overlay_text="Override active",
        warning_text="",
    ),
    "error": ModeRule(
        layout_density="normal",
        nonessential_opacity=0.45,
        spacing=10,
        panel_visibility={"actions": True, "status": True, "session": True},
        overlay_text="",
        warning_text="System attention needed",
    ),
}

def _time_of_day(now: datetime) -> str:
    hour = now.hour
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "night"

def _attention_level(focus: float, stress: float, energy: float) -> str:
    if stress >= 0.7 or energy <= 0.35:
        return "low"
    if focus >= 0.7 and energy >= 0.6 and stress <= 0.5:
        return "high"
    return "med"

def _apply_mode_effective(runtime: AuroraRuntimeState) -> str:
    if runtime.error_active:
        return "error"
    if runtime.dnd_active or runtime.current_mode == "blocked":
        return "blocked"
    if runtime.current_mode in MODE_RULES:
        return runtime.current_mode
    return "idle"

def _filter_actions(
    registry: ActionRegistry,
    runtime: AuroraRuntimeState,
    mode: str,
) -> List[ActionItem]:
    "'''
    Return mode-appropriate actions, filtered for session/DND rules.

    This function must be extremely defensive because ActionRegistry can be
    partially loaded in sparse / packaging contexts.
    '''
    try:
        registry_actions = registry.list_actions()
    except RecursionError:
        registry_actions = getattr(registry, "_actions", [])
    except Exception:
        registry_actions = getattr(registry, "_actions", [])

    actions: List[ActionSpec] = []
    for action in list(registry_actions or []):
        try:
            if getattr(action, "requires_session", False) and not runtime.session_active:
                continue
            if runtime.dnd_active and getattr(action, "dnd_blocked", False):
                continue
            actions.append(action)
        except Exception:
            continue

    actions.sort(key=lambda item: getattr(item, "priority", 0))

    if mode == "idle":
        actions = actions[:3]
    elif mode == "focus":
        actions = [a for a in actions if getattr(a, "category", "") in ("mode", "workspace")]
    elif mode == "break":
        actions = [a for a in actions if getattr(a, "category", "") in ("mode", "override", "workspace")]
    elif mode == "blocked":
        actions = [a for a in actions if getattr(a, "category", "") == "override"]
    elif mode == "error":
        actions = [a for a in actions if getattr(a, "category", "") != "mode"]

    return [
        ActionItem(
            action_id=str(getattr(action, "action_id", "")),
            label=str(getattr(action, "label", getattr(action, "action_id", ""))) ,
            intent=str(getattr(action, "intent", "")),
            enabled=not (runtime.dnd_active and getattr(action, "dnd_blocked", False)),
        )
        for action in actions
        if getattr(action, "action_id", None)
    ]

def compute_canvas_state(
    runtime: AuroraRuntimeState,
    registry: ActionRegistry,
    now: Optional[datetime] = None,
) -> AuroraCanvasState:
    now = now or datetime.now()
    effective_mode = _apply_mode_effective(runtime)
    rule = MODE_RULES.get(effective_mode, MODE_RULES["idle"])
    attention = _attention_level(runtime.focus, runtime.stress, runtime.energy)
    theme_profile = {
        "time_of_day": _time_of_day(now),
        "emotion_tag": runtime.emotion_tag,
        "reduce_motion": runtime.reduce_motion,
    }
    actions = _filter_actions(registry, runtime, effective_mode)

    return AuroraCanvasState(
        current_mode=effective_mode,
        focus=runtime.focus,
        stress=runtime.stress,
        energy=runtime.energy,
        workspace_id=runtime.workspace_id,
        workspace_name=runtime.workspace_name,
        session_active=runtime.session_active,
        layout_density=rule.layout_density,
        attention_level=attention,
        suggested_actions=actions,
        theme_profile=theme_profile,
        nonessential_opacity=rule.nonessential_opacity,
        spacing=rule.spacing,
        panel_visibility=rule.panel_visibility,
        overlay_text=rule.overlay_text,
        warning_text=rule.warning_text,
        last_saved=runtime.last_saved,
    )


class AuroraStateStore:
    def __init__(self, registry: ActionRegistry):
        self._registry = registry
        self._runtime = AuroraRuntimeState()
        self._listeners: List[Callable[[AuroraCanvasState], None]] = []

    @property
    def runtime(self) -> AuroraRuntimeState:
        return self._runtime

    def subscribe(self, listener: Callable[[AuroraCanvasState], None]) -> None:
        self._listeners.append(listener)

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self._runtime, key):
                setattr(self._runtime, key, value)
        self.notify()

    def notify(self) -> None:
        state = compute_canvas_state(self._runtime, self._registry)
        for listener in self._listeners:
            listener(state)

    def get_canvas_state(self) -> AuroraCanvasState:
        return compute_canvas_state(self._runtime, self._registry)