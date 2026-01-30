from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Any, Optional

from corund.workspace_ai.router import WorkspaceAIRouter
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
    """
    Connects AI routing -> real WorkspaceManager actions.

    Final demo:
      - unified command pipeline for UI + voice (source tracked)
      - mode switch emits signals.mode_changed
      - focus timer emits focus_* signals for UI and avatar persona
      - self-awareness explain command for professor-friendly output
    """

    def __init__(self, workspace_manager):
        self.wm = workspace_manager
        self.router = WorkspaceAIRouter()
        self.hub = WorkspaceAIHub()
        self.active_mode = "study"
        self.focus = FocusTimerState()

    def handle_command(self, text: str, *, source: str = "ui") -> Dict[str, Any]:
        t = (text or "").strip()
        route = self.router.route(t)
        action = route.get("action")
        payload = route.get("payload") or {}

        meta = {"source": source, "ts": route.get("ts")}

        # broadcast (new + legacy)
        if signals is not None:
            try:
                if hasattr(signals, "command_received_ex"):
                    signals.command_received_ex.emit(t, meta)
                if hasattr(signals, "command_received"):
                    signals.command_received.emit(t)
            except Exception:
                pass

        # ---- greet ----
        if action == "greet":
            reply = "Hi 👋 I’m Etherea. Tell me a mode (study/coding/exam/calm) or say 'focus 25'."
            return {"ok": True, "action": "greet", "reply": reply, "meta": meta}

        # ---- mode switch ----
        if action == "set_mode":
            mode = str(payload.get("mode", "study"))
            return self.apply_mode(mode, meta=meta)

        # ---- save session ----
        if action == "save_session":
            path = self.wm.save_session()
            return {"ok": True, "action": "save_session", "file": path, "meta": meta}

        # ---- resume session ----
        if action == "resume_session":
            result = self.wm.resume_last_session()
            return {"ok": True, "action": "resume_session", "result": result, "meta": meta}

        # ---- focus timer ----
        if action == "start_focus_timer":
            minutes = int(payload.get("minutes", 25))
            return self.start_focus(minutes, meta=meta)

        if action == "stop_focus_timer":
            return self.stop_focus(meta=meta)

        # ---- summarize text (simple local) ----
        if action == "summarize_text":
            txt = payload.get("text", "")
            summary = self._quick_summary(txt)
            return {"ok": True, "action": "summarize_text", "summary": summary, "meta": meta}

        # ---- self explain ----
        if action == "self_explain":
            if build_self_explain_text is None:
                explain = self._static_self_explain()
            else:
                explain = build_self_explain_text()
            return {"ok": True, "action": "self_explain", "text": explain, "meta": meta}

        # ---- unknown ----
        return {"ok": False, "action": "unknown", "text": t, "meta": meta}

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

        return {
            "ok": True,
            "action": "set_mode",
            "mode": mode,
            "profile": profile,
            "ai_plan": {"mode": getattr(plan, "mode", mode), "tasks": getattr(plan, "tasks", [])},
            "meta": meta,
        }

    def start_focus(self, minutes: int, *, meta: Optional[dict] = None) -> Dict[str, Any]:
        meta = meta or {"source": "ui"}
        minutes = max(1, min(240, int(minutes)))
        now = time.time()
        self.focus = FocusTimerState(True, minutes, now, now + minutes * 60)

        # mode hint: deep_work
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
            "- UI: PySide6 (main_window_v2.py) with Avatar + Aurora + Console.\n"
            "- Workspace: WorkspaceManager + adapters (PDF/code/text) + AI routing.\n"
            "- Avatar: emotional persona driven by EI signals + mode.\n"
            "- Voice: STT (SpeechRecognition) + TTS (Edge TTS) routed into the same command pipeline.\n"
            "Ask: 'study mode', 'coding mode', 'exam mode', 'calm mode', or 'focus 25'."
)
