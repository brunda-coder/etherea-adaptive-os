from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from corund.app_runtime import user_data_dir
from corund.database import db

_ALLOWED_SUFFIXES = {".md", ".py", ".js", ".java", ".cpp", ".yaml", ".yml", ".mmd", ".txt"}


@dataclass
class AgentResult:
    ok: bool
    action: str
    message: str
    content: Optional[str] = None


class SafeWorkspaceFileAgent:
    """Capability-based local file agent with default-deny outside allowed roots."""

    def __init__(self) -> None:
        self.config_path = user_data_dir() / "workspace_agent_roots.json"
        self.allowed_roots = self._load_allowed_roots()

    def _load_allowed_roots(self) -> List[Path]:
        profile = db.get_profile_context() or {}
        raw = profile.get("workspace_allowed_roots")
        roots: List[Path] = []
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    roots = [Path(p).expanduser().resolve() for p in parsed if isinstance(p, str)]
            except Exception:
                roots = []
        if not roots:
            default = (Path.cwd() / "workspace").resolve()
            default.mkdir(parents=True, exist_ok=True)
            roots = [default]
            db.set_preference("workspace_allowed_roots", json.dumps([str(default)]))
        return roots

    def configure_allowed_roots(self, roots: List[str]) -> None:
        normalized = [str(Path(p).expanduser().resolve()) for p in roots if p]
        if not normalized:
            return
        db.set_preference("workspace_allowed_roots", json.dumps(normalized))
        self.allowed_roots = [Path(p) for p in normalized]

    def _resolve(self, rel_or_abs: str) -> Path:
        p = Path(rel_or_abs).expanduser()
        if not p.is_absolute():
            p = self.allowed_roots[0] / p
        return p.resolve()

    def _is_allowed(self, path: Path) -> bool:
        for root in self.allowed_roots:
            try:
                path.relative_to(root)
                return True
            except ValueError:
                continue
        return False

    def _validate_suffix(self, path: Path) -> bool:
        return path.suffix.lower() in _ALLOWED_SUFFIXES

    def create_file(self, path_text: str, content: str = "") -> AgentResult:
        path = self._resolve(path_text)
        if not self._is_allowed(path):
            return AgentResult(False, "create_file", "Denied: path is outside allowed workspace roots.")
        if not self._validate_suffix(path):
            return AgentResult(False, "create_file", "Denied: unsupported file type.")
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return AgentResult(False, "create_file", "File already exists.")
        path.write_text(content or "", encoding="utf-8")
        return AgentResult(True, "create_file", f"Created {path}")

    def edit_file(self, path_text: str, content: str) -> AgentResult:
        path = self._resolve(path_text)
        if not self._is_allowed(path):
            return AgentResult(False, "edit_file", "Denied: path is outside allowed workspace roots.")
        if not self._validate_suffix(path):
            return AgentResult(False, "edit_file", "Denied: unsupported file type.")
        if not path.exists():
            return AgentResult(False, "edit_file", "File not found.")
        path.write_text(content, encoding="utf-8")
        return AgentResult(True, "edit_file", f"Updated {path}")

    def summarize_file(self, path_text: str) -> AgentResult:
        path = self._resolve(path_text)
        if not self._is_allowed(path):
            return AgentResult(False, "summarize_file", "Denied: path is outside allowed workspace roots.")
        if not path.exists():
            return AgentResult(False, "summarize_file", "File not found.")
        raw = path.read_text(encoding="utf-8", errors="ignore")
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()][:8]
        summary = "\n".join(f"• {ln[:140]}" for ln in lines) if lines else "• (empty file)"
        return AgentResult(True, "summarize_file", f"Summary for {path.name}", content=summary)
