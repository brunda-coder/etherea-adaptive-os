from __future__ import annotations

from dataclasses import dataclass, asdict, field
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json


@dataclass
class WorkspaceRecord:
    workspace_id: str
    name: str
    workspace_type: str
    path: str
    created_at: str
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

    def _load(self) -> None:
        if self.state_path.exists():
            self._state = json.loads(self.state_path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self.state_path.write_text(json.dumps(self._state, indent=2), encoding="utf-8")

    def _now(self) -> str:
        return datetime.utcnow().isoformat()

    def list_workspaces(self) -> List[WorkspaceRecord]:
        records: List[WorkspaceRecord] = []
        for item in self._state.get("workspaces", []):
            payload = {
                "workspace_id": item.get("workspace_id"),
                "name": item.get("name"),
                "workspace_type": item.get("workspace_type", "general"),
                "path": item.get("path"),
                "created_at": item.get("created_at"),
                "last_opened": item.get("last_opened"),
                "last_saved": item.get("last_saved"),
                "session_data": item.get("session_data") or {},
            }
            if payload["workspace_id"] and payload["name"]:
                records.append(WorkspaceRecord(**payload))
        return records
        return [WorkspaceRecord(**item) for item in self._state.get("workspaces", [])]

    def get_current(self) -> Optional[WorkspaceRecord]:
        current_id = self._state.get("current_id")
        if not current_id:
            return None
        return self.get_workspace(str(current_id))

    def get_workspace(self, workspace_id: str) -> Optional[WorkspaceRecord]:
        for item in self._state.get("workspaces", []):
            if item.get("workspace_id") == workspace_id:
                return WorkspaceRecord(**item)
        return None

    def create_workspace(self, name: Optional[str] = None) -> WorkspaceRecord:
        existing = self.list_workspaces()
        next_index = len(existing) + 1
        workspace_id = f"ws_{int(datetime.utcnow().timestamp())}_{next_index}"
        workspace_name = name or f"Workspace {next_index}"
        workspace_path = self.root / workspace_id
        workspace_path.mkdir(parents=True, exist_ok=True)
        record = WorkspaceRecord(
            workspace_id=workspace_id,
            name=workspace_name,
            workspace_type="general",
            path=str(workspace_path),
            created_at=self._now(),
            session_data={},
        )
        self._state["workspaces"] = [asdict(ws) for ws in existing] + [asdict(record)]
        self._state["current_id"] = workspace_id
        self._save()
        return record

    def open_workspace(self, workspace_id: str) -> Optional[WorkspaceRecord]:
        workspaces = self.list_workspaces()
        updated: List[dict] = []
        selected: Optional[WorkspaceRecord] = None
        for ws in workspaces:
            if ws.workspace_id == workspace_id:
                ws.last_opened = self._now()
                selected = ws
            updated.append(asdict(ws))
        if selected:
            self._state["workspaces"] = updated
            self._state["current_id"] = workspace_id
            self._save()
        return selected

    def resume_last(self) -> Optional[WorkspaceRecord]:
        current = self.get_current()
        if current:
            return current
        workspaces = self.list_workspaces()
        if not workspaces:
            return None
        latest = sorted(
            workspaces,
            key=lambda ws: ws.last_opened or ws.last_saved or ws.created_at,
            reverse=True,
        )[0]
        return self.open_workspace(latest.workspace_id)

    def save_snapshot(self, payload: Dict[str, object]) -> Optional[Path]:
        current = self.get_current()
        if not current:
            return None
        snapshot_path = Path(current.path) / "snapshot.json"
        snapshot = {
            "workspace_id": current.workspace_id,
            "name": current.name,
            "saved_at": self._now(),
            "payload": payload,
        }
        snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
        self._touch_saved(current.workspace_id, snapshot["saved_at"], payload)
        return snapshot_path

    def _touch_saved(self, workspace_id: str, timestamp: str, payload: Dict[str, object]) -> None:
        self._touch_saved(current.workspace_id, snapshot["saved_at"])
        return snapshot_path

    def _touch_saved(self, workspace_id: str, timestamp: str) -> None:
        workspaces = self.list_workspaces()
        updated: List[dict] = []
        for ws in workspaces:
            if ws.workspace_id == workspace_id:
                ws.last_saved = timestamp
                ws.session_data = payload
            updated.append(asdict(ws))
        self._state["workspaces"] = updated
        self._save()
