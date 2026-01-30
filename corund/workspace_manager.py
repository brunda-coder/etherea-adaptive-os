"""
Unified Workspace Manager (Foundation)
- Single workspace for all file types (no split)
- Adapter-based extensibility
- Per-file agent attachment
- Seal/unseal workspace (read-only vs editable)
- Unified save system
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Any

from corund.workspace_ai.session_memory import save_snapshot, load_snapshot
from corund.adapters import get_adapter_for_path
from corund.agents import get_agent_for_adapter

@dataclass
class OpenFile:
    path: Path
    adapter: Any
    agent: Any
    sealed: bool = False

class WorkspaceManager:
    def __init__(self, root: str = "workspace"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.open_files: Dict[str, OpenFile] = {}

    def open(self, filepath: str) -> OpenFile:
        p = Path(filepath)
        if not p.is_absolute():
            p = self.root / p

        adapter = get_adapter_for_path(p)
        adapter.read()
        agent = get_agent_for_adapter(adapter)

        f = OpenFile(path=p, adapter=adapter, agent=agent, sealed=False)
        self.open_files[str(p)] = f
        return f

    def seal(self, filepath: str):
        f = self._get(filepath)
        f.sealed = True
        f.adapter.set_readonly(True)

    def unseal(self, filepath: str):
        f = self._get(filepath)
        f.sealed = False
        f.adapter.set_readonly(False)

    def write(self, filepath: str, content: Any):
        f = self._get(filepath)
        if f.sealed:
            raise PermissionError("Workspace file is sealed (read-only).")
        f.adapter.write(content)

    def save(self, filepath: str):
        f = self._get(filepath)
        f.adapter.save()

    def highlight(self, filepath: str, pattern: str):
        f = self._get(filepath)
        return f.agent.highlight(pattern)

    def analyse(self, filepath: str):
        f = self._get(filepath)
        return f.agent.analyse()

    def _get(self, filepath: str) -> OpenFile:
        p = Path(filepath)
        if not p.is_absolute():
            p = self.root / p
        key = str(p)
        if key not in self.open_files:
            return self.open(key)
        return self.open_files[key]

    # =========================
    # Session Memory (NEW)
    # =========================
    def get_session_snapshot(self) -> dict:
        """Return a lightweight snapshot of open workspace state."""
        files = []
        for key, f in self.open_files.items():
            files.append({
                "path": str(f.path),
                "sealed": bool(getattr(f, "sealed", False))
            })
        return {
            "open_files": files,
            "notes": "auto-saved workspace session"
        }

    def save_session(self) -> str:
        """Persist the latest snapshot to workspace/.etherea_last_session.json"""
        snap = self.get_session_snapshot()
        out = save_snapshot(snap)
        return str(out)

    def resume_last_session(self) -> dict:
        """Reopen last session's open files and restore sealed state."""
        snap = load_snapshot()
        restored = {"opened": 0, "sealed": 0, "missing": 0}

        open_files = snap.get("open_files") or []
        for item in open_files:
            path = item.get("path")
            sealed = bool(item.get("sealed", False))
            if not path:
                continue

            try:
                # open() normalizes workspace-relative paths internally
                f = self.open(path)
                restored["opened"] += 1

                if sealed:
                    try:
                        self.seal(path)
                        restored["sealed"] += 1
                    except Exception:
                        pass

            except Exception:
                restored["missing"] += 1

        return restored

