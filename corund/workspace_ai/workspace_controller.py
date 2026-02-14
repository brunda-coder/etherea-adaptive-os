from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Any, Optional

from corund.workspace_ai.router import WorkspaceAIRouter
from corund.workspace_ai.safe_file_agent import SafeWorkspaceFileAgent
from corund.workspace_ai.workspace_ai_hub import WorkspaceAIHub

try:
    from corund.signals import signals
except Exception:
    signals = None

try:
    from corund.self_awareness.introspector import build_self_explain_text
except Exception:
    build_self_explain_text = None


@dataclass
class FocusTimerState:
    running: bool = False
    minutes: int = 0
    started_at: float = 0.0
    ends_at: float = 0.0

    def seconds_left(self) -> int:
        if not self.running:
            return 0
        return max(0, int(self.ends_at - time.time()))


class WorkspaceController:
    def __init__(self, workspace_manager):
        self.wm = workspace_manager
        self.router = WorkspaceAIRouter()
        self.hub = WorkspaceAIHub()
        self.file_agent = SafeWorkspaceFileAgent()
        self.active_mode = "study"
        self.focus = FocusTimerState()

    def handle_command(self, text: str, *, source: str = "ui") -> Dict[str, Any]:
        t = (text or "").strip()
        route = self.router.route(t)
        action = route.get("action")
        payload = route.get("payload") or {}
        meta = {"source": source, "ts": route.get("ts")}

        if signals is not None:
            try:
                if hasattr(signals, "command_received_ex"):
                    signals.command_received_ex.emit(t, meta)
                if hasattr(signals, "command_received"):
                    signals.command_received.emit(t)
            except Exception:
                pass

        if action == "greet":
            reply = "Hi 👋 I’m Etherea. Tell me a mode (study/coding/exam/calm), 'focus 25', or 'create file notes.md'."
            return {"ok": True, "action": "greet", "reply": reply, "meta": meta}
        if action == "open_aurora":
            return {"ok": True, "action": "open_aurora", "panel": "aurora", "meta": meta}
        if action == "open_workspace":
            return {"ok": True, "action": "open_workspace", "panel": "workspace", "meta": meta}
        if action == "open_agent_works":
            return {"ok": True, "action": "open_agent_works", "panel": "agent", "meta": meta}
        if action == "set_mode":
            return self.apply_mode(str(payload.get("mode", "study")), meta=meta)
        if action == "save_session":
            path = self.wm.save_session()
            return {"ok": True, "action": "save_session", "file": path, "meta": meta}
        if action == "resume_session":
            result = self.wm.resume_last_session()
            return {"ok": True, "action": "resume_session", "result": result, "meta": meta}
        if action == "start_focus_timer":
            return self.start_focus(int(payload.get("minutes", 25)), meta=meta)
        if action == "stop_focus_timer":
            return self.stop_focus(meta=meta)
        if action == "summarize_text":
            return {"ok": True, "action": "summarize_text", "summary": self._quick_summary(payload.get("text", "")), "meta": meta}
        if action == "self_explain":
            explain = build_self_explain_text() if build_self_explain_text is not None else self._static_self_explain()
            return {"ok": True, "action": "self_explain", "text": explain, "meta": meta}

        if action == "allow_workspace_root":
            root = str(payload.get("root", "")).strip()
            self.file_agent.configure_allowed_roots([root])
            return {"ok": True, "action": action, "message": f"Allowed workspace root set to {root}", "meta": meta}
        if action == "create_file":
            res = self.file_agent.create_file(str(payload.get("path", "")), str(payload.get("content", "")))
            return {"ok": res.ok, "action": action, "message": res.message, "meta": meta}
        if action == "edit_file":
            res = self.file_agent.edit_file(str(payload.get("path", "")), str(payload.get("content", "")))
            return {"ok": res.ok, "action": action, "message": res.message, "meta": meta}
        if action == "summarize_file":
            res = self.file_agent.summarize_file(str(payload.get("path", "")))
            return {"ok": res.ok, "action": action, "message": res.message, "summary": res.content, "meta": meta}
        if action == "list_workspace_files":
            res = self.file_agent.list_workspace_files(depth=int(payload.get("depth", 2)))
            return {"ok": res.ok, "action": action, "message": res.message, "files": res.content, "meta": meta}

        return {"ok": False, "action": "unknown", "text": t, "message": "I can route workspace, focus, and safe file commands.", "meta": meta}

    def apply_mode(self, mode: str, *, meta: Optional[dict] = None) -> Dict[str, Any]:
        meta = meta or {"source": "ui"}
        self.active_mode = mode
        profile = self.hub.get_profile(mode) or {}
        plan = self.hub.plan(f"{mode} mode")
        try:
            self.wm.active_mode = mode
            self.wm.active_profile = profile
        except Exception:
            pass
        if signals is not None and hasattr(signals, "mode_changed"):
            try:
                signals.mode_changed.emit(mode, meta)
            except Exception:
                pass
        return {"ok": True, "action": "set_mode", "mode": mode, "profile": profile, "ai_plan": {"mode": getattr(plan, "mode", mode), "tasks": getattr(plan, "tasks", [])}, "meta": meta}

    def start_focus(self, minutes: int, *, meta: Optional[dict] = None) -> Dict[str, Any]:
        meta = meta or {"source": "ui"}
        minutes = max(1, min(240, int(minutes)))
        now = time.time()
        self.focus = FocusTimerState(True, minutes, now, now + minutes * 60)
        try:
            self.apply_mode("deep_work", meta={**meta, "reason": "focus_started"})
        except Exception:
            pass
        if signals is not None and hasattr(signals, "focus_started"):
            try:
                signals.focus_started.emit(minutes, meta)
            except Exception:
                pass
        return {"ok": True, "action": "start_focus_timer", "minutes": minutes, "ends_in_s": minutes * 60, "meta": meta}

    def stop_focus(self, *, meta: Optional[dict] = None) -> Dict[str, Any]:
        meta = meta or {"source": "ui"}
        was_running = bool(self.focus.running)
        self.focus.running = False
        if signals is not None and hasattr(signals, "focus_stopped"):
            try:
                signals.focus_stopped.emit({**meta, "was_running": was_running})
            except Exception:
                pass
        return {"ok": True, "action": "stop_focus_timer", "was_running": was_running, "meta": meta}

    def focus_seconds_left(self) -> int:
        return self.focus.seconds_left()

    def _quick_summary(self, text: str) -> str:
        t = (text or "").strip()
        if not t:
            return ""
        lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
        return " • " + "\n • ".join(lines[:5])

    def _static_self_explain(self) -> str:
        return (
            "Etherea is a desktop-first living OS prototype.\n"
            "- UI: PySide6 with Avatar + Aurora + Settings.\n"
            "- Workspace: WorkspaceManager + local file agent (allowed roots only).\n"
            "- Avatar: emotion-aware character responses through offline brain.json.\n"
            "- Voice/Sensors: opt-in controls with kill switch in settings."
        )
