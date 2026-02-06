from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class WorkspacePlan:
    mode: str
    tasks: list[str]


class WorkspaceAIHub:
    """Loads workspace profiles and returns lightweight planning hints."""

    def __init__(self):
        self.profiles: Dict[str, Any] = self._load_profiles()

    def _load_profiles(self) -> Dict[str, Any]:
        json_path = Path(__file__).with_name("workspace_profiles.json")
        print(f"AI_HUB: Loading workspace profiles from: {json_path}")

        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            print(f"ERROR: AI Hub - The profiles file was not found at {json_path}")
            return {}
        except json.JSONDecodeError:
            print(f"ERROR: AI Hub - The profiles file at {json_path} is not valid JSON.")
            return {}

        # Support both old schema ({"profiles": {...}}) and flattened schema ({"study": {...}}).
        if isinstance(data, dict) and "profiles" in data and isinstance(data["profiles"], dict):
            return data["profiles"]
        if isinstance(data, dict):
            return data

        print("ERROR: AI Hub - profiles payload is not a dictionary.")
        return {}

    def get_profile(self, workspace_name: str) -> Dict[str, Any]:
        return self.profiles.get(workspace_name, self.profiles.get("default", {}))

    def plan(self, command_text: str) -> WorkspacePlan:
        mode = (command_text or "").split()[0].strip().lower() or "study"
        profile = self.get_profile(mode)
        tasks = [
            f"Set ring mode: {profile.get('ring_mode', mode)}",
            f"Set avatar tone: {profile.get('avatar_tone', 'supportive')}",
            f"Apply layout: {profile.get('ui_layout', 'default')}",
        ]
        return WorkspacePlan(mode=mode, tasks=tasks)


_ai_hub_instance = None


def get_ai_hub():
    global _ai_hub_instance
    if _ai_hub_instance is None:
        _ai_hub_instance = WorkspaceAIHub()
    return _ai_hub_instance
