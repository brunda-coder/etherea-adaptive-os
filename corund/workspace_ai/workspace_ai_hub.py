from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional
import json

from corund.workspace_ai.focus_mode import detect_focus_mode
from corund.workspace_ai.task_extractor import extract_tasks


@dataclass
class WorkspaceAIResult:
    mode: str
    tasks: list
    notes: str = ""


class WorkspaceAIHub:
    """
    AI-like features without requiring LLM installs.
    Later we can plug OpenAI locally in desktop builds.
    """

    def __init__(self, profiles_path: str = "core/workspace_ai/workspace_profiles.json"):
        self.profiles_path = Path(profiles_path)
        self.profiles: Dict[str, Any] = {}
        self.load_profiles()

    def load_profiles(self):
        try:
            self.profiles = json.loads(self.profiles_path.read_text(encoding="utf-8"))
        except Exception:
            self.profiles = {}

    def plan(self, user_text: str) -> WorkspaceAIResult:
        mode = detect_focus_mode(user_text)
        tasks = extract_tasks(user_text)

        return WorkspaceAIResult(
            mode=mode,
            tasks=tasks,
            notes=f"workspace_mode={mode}"
        )

    def get_profile(self, mode: str) -> Optional[Dict[str, Any]]:
        return self.profiles.get(mode)
