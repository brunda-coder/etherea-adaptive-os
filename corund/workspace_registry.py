from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Literal
import json

# As per the blueprint, these are the only valid workspace types.
WorkspaceType = Literal["Study", "Build", "Research", "Calm", "Deep Work"]

CORE_WORKSPACES = {
    "Study": "A quiet space for deep learning and concentration.",
    "Build": "A dynamic environment for coding, creating, and compiling.",
    "Research": "A space for browsing, collecting, and analyzing information.",
    "Calm": "A minimal, serene space for relaxation and mindfulness.",
    "Deep Work": "An immersive, distraction-free environment for intense focus."
}

@dataclass
class WorkspaceRecord:
    workspace_id: str
    name: str # This is now one of the CORE_WORKSPACES keys
    workspace_type: WorkspaceType
    path: str
    created_at: str
    description: str
    last_opened: Optional[str] = None
    last_saved: Optional[str] = None
    session_data: Dict[str, object] = field(default_factory=dict)


class WorkspaceRegistry:
    def __init__(self, root: str = "workspace"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.state_path = self.root / ".etherea_workspaces.json"
        self._state: Dict[str, object] = {"workspaces": [], "current_id": None}
        self._load()
        self._initialize_core_workspaces()

    def _load(self) -> None:
        if self.state_path.exists():
            self._state = json.loads(self.state_path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self.state_path.write_text(json.dumps(self._state, indent=2), encoding="utf-8")

    def _now(self) -> str:
        return datetime.utcnow().isoformat()
    
    def _initialize_core_workspaces(self):
        """Ensures that the five core workspaces exist in the registry."""
        existing_workspaces = {ws.name: ws for ws in self.list_workspaces()}
        needs_save = False
        for name, description in CORE_WORKSPACES.items():
            if name not in existing_workspaces:
                self._create_workspace_record(name, description)
                needs_save = True
        if needs_save:
            self._save()
    
    def _create_workspace_record(self, name: str, description: str) -> WorkspaceRecord:
        """Internal helper to create a workspace record without saving immediately."""
        workspace_id = f"ws_{name.lower().replace(' ', '_')}"
        workspace_path = self.root / workspace_id
        workspace_path.mkdir(parents=True, exist_ok=True)
        record = WorkspaceRecord(
            workspace_id=workspace_id,
            name=name,
            workspace_type=name, # The type is the name
            path=str(workspace_path),
            created_at=self._now(),
            description=description
        )
        workspaces = self.list_workspaces()
        self._state["workspaces"] = [asdict(ws) for ws in workspaces] + [asdict(record)]
        return record

    def list_workspaces(self) -> List[WorkspaceRecord]:
        """Lists all available workspaces, which are the five core ones."""
        records: List[WorkspaceRecord] = []
        for item in self._state.get("workspaces", []):
            # Basic validation
            if item.get("workspace_id") and item.get("name") in CORE_WORKSPACES:
                records.append(WorkspaceRecord(**item))
        return records

    def get_current(self) -> Optional[WorkspaceRecord]:
        current_id = self._state.get("current_id")
        if not current_id:
            # Default to the 'Calm' workspace if none is selected
            calm_ws = self.get_workspace_by_name("Calm")
            if calm_ws:
                self._state["current_id"] = calm_ws.workspace_id
                return calm_ws
            return None
        return self.get_workspace(str(current_id))

    def get_workspace(self, workspace_id: str) -> Optional[WorkspaceRecord]:
        for ws in self.list_workspaces():
            if ws.workspace_id == workspace_id:
                return ws
        return None
    
    def get_workspace_by_name(self, name: WorkspaceType) -> Optional[WorkspaceRecord]:
        for ws in self.list_workspaces():
            if ws.name == name:
                return ws
        return None

    def switch_workspace(self, workspace_name: WorkspaceType) -> Optional[WorkspaceRecord]:
        """Switches the current workspace to the one specified by name."""
        ws_to_activate = self.get_workspace_by_name(workspace_name)
        if ws_to_activate:
            self._state["current_id"] = ws_to_activate.workspace_id
            ws_to_activate.last_opened = self._now()
            # Update the record in the state
            all_ws = [asdict(w) for w in self.list_workspaces() if w.workspace_id != ws_to_activate.workspace_id] + [asdict(ws_to_activate)]
            self._state["workspaces"] = all_ws
            self._save()
            return ws_to_activate
        return None
