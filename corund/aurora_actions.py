from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class ActionSpec:
    action_id: str
    label: str
    intent: str
    modes: tuple[str, ...]
    category: str
    priority: int = 50
    requires_session: bool = False
    dnd_blocked: bool = True


class ActionRegistry:
    def __init__(self, actions: Iterable[ActionSpec]):
        self._actions = list(actions)
        self._index = {action.action_id: action for action in self._actions}

    @classmethod
    def default(cls) -> "ActionRegistry":
        return cls(
            [
                ActionSpec(
                    action_id="set_mode_idle",
                    label="Idle Mode",
                    intent="set_mode_idle",
                    modes=("all",),
                    category="mode",
                    priority=10,
                    dnd_blocked=False,
                ),
                ActionSpec(
                    action_id="set_mode_focus",
                    label="Focus Mode",
                    intent="set_mode_focus",
                    modes=("all",),
                    category="mode",
                    priority=11,
                    dnd_blocked=False,
                ),
                ActionSpec(
                    action_id="set_mode_break",
                    label="Break Mode",
                    intent="set_mode_break",
                    modes=("all",),
                    category="mode",
                    priority=12,
                    dnd_blocked=False,
                ),
                ActionSpec(
                    action_id="workspace_create",
                    label="Create Workspace",
                    intent="workspace_create",
                    modes=("idle", "focus", "break"),
                    category="workspace",
                    priority=20,
                ),
                ActionSpec(
                    action_id="workspace_resume",
                    label="Resume Workspace",
                    intent="workspace_resume",
                    modes=("idle", "focus", "break"),
                    category="workspace",
                    priority=21,
                    dnd_blocked=False,
                ),
                ActionSpec(
                    action_id="workspace_save_snapshot",
                    label="Save Snapshot",
                    intent="workspace_save_snapshot",
                    modes=("idle", "focus", "break"),
                    category="workspace",
                    priority=22,
                    requires_session=True,
                ),
                ActionSpec(
                    action_id="os_open_workspace_folder",
                    label="Open Workspace Folder",
                    intent="os_open_workspace_folder",
                    modes=("idle", "focus", "break"),
                    category="os",
                    priority=23,
                    requires_session=True,
                ),
                ActionSpec(
                    action_id="toggle_dnd_on",
                    label="Enable DND",
                    intent="toggle_dnd_on",
                    modes=("idle", "focus", "break"),
                    category="override",
                    priority=30,
                    dnd_blocked=False,
                ),
                ActionSpec(
                    action_id="create_presentation",
                    label="Create Presentation",
                    intent="create_ppt",
                    modes=("idle", "focus", "break"),
                    category="workspace",
                    priority=24,
                    dnd_blocked=False,
                ),
                ActionSpec(
                    action_id="toggle_dnd_off",
                    label="Override DND",
                    intent="toggle_dnd_off",
                    modes=("blocked", "error"),
                    category="override",
                    priority=1,
                    dnd_blocked=False,
                ),
            ]
        )

    def list_actions(self) -> List[ActionSpec]:
        return list(self._actions)

    def get(self, action_id: str) -> Optional[ActionSpec]:
        return self._index.get(action_id)

    def action_for_intent(self, intent: str) -> Optional[ActionSpec]:
        intent_aliases = {"create_presentation": "create_ppt", "ppt": "create_ppt"}
        normalized = intent_aliases.get(intent, intent)
        for action in self._actions:
            if action.intent == normalized:
                return action
        return None
