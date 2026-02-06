from __future__ import annotations

from typing import Dict, Any
import time


class WorkspaceAIRouter:
    """
    Simple command router for workspace actions.
    Termux-safe, no heavy dependencies.

    Final demo additions:
      - stop focus timer
      - hello etherea / wake commands
      - self-explain command
      - focus duration parsing without explicit "minutes"
    """

    def route(self, text: str) -> Dict[str, Any]:
        t = (text or "").strip()
        low = t.lower().strip()

        # ---- wake / greeting ----
        if low in ("hello etherea", "hi etherea", "hey etherea", "etherea"):
            return self._action("greet", {"text": t})

        # ---- self awareness ----
        if "explain yourself" in low or "how were you built" in low or "how you were built" in low:
            return self._action("self_explain", {"query": t})

        # ---- mode switches ----

        # ---- home voice-first commands ----
        if low in ("open aurora", "show aurora"):
            return self._action("open_aurora", {"target": "aurora"})

        if low in ("open workspace", "show workspace"):
            return self._action("open_workspace", {"target": "workspace"})

        if low in ("open agent works", "open agent", "agent works"):
            return self._action("open_agent_works", {"target": "agent"})

        if low.startswith("switch to "):
            raw = low.replace("switch to ", "", 1).replace(" mode", "").strip()
            alias = {
                "drawing": "study",
                "pdf": "research",
                "pdf/office": "research",
                "office": "research",
                "coding": "coding",
            }
            mapped = alias.get(raw, raw)
            return self._action("set_mode", {"mode": mapped, "requested_mode": raw})
        for mode in ["study", "coding", "exam", "calm", "deep_work", "meeting"]:
            if low == mode or f"{mode} mode" in low or low.startswith(f"set {mode}"):
                return self._action("set_mode", {"mode": mode})

        # ---- session commands ----
        if "save session" in low or "store session" in low:
            return self._action("save_session", {})

        if "continue last session" in low or "resume session" in low or "continue session" in low:
            return self._action("resume_session", {})

        # ---- focus timer ----
        # stop focus / cancel timer
        if "stop focus" in low or "cancel focus" in low or low == "stop timer" or low == "cancel timer":
            return self._action("stop_focus_timer", {})

        # start focus timer:
        # "focus 25", "focus for 25", "focus 25 minutes"
        if low.startswith("focus"):
            minutes = self._extract_int(low) or 25
            return self._action("start_focus_timer", {"minutes": minutes})

        # ---- summary ----
        if low.startswith("summarize"):
            return self._action("summarize_text", {"text": t})

        # ---- fallback ----
        return self._action("unknown", {"text": t})

    def _action(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"action": name, "payload": payload, "ts": time.time()}

    def _extract_int(self, s: str):
        num = ""
        for ch in s:
            if ch.isdigit():
                num += ch
            elif num:
                break
        return int(num) if num else None
