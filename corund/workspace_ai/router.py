from __future__ import annotations

from typing import Dict, Any
import re
import time


class WorkspaceAIRouter:
    """Local command router for workspace and safe file-agent actions."""

    def route(self, text: str) -> Dict[str, Any]:
        t = (text or "").strip()
        low = t.lower().strip()

        if low in ("hello etherea", "hi etherea", "hey etherea", "etherea"):
            return self._action("greet", {"text": t})

        if "explain yourself" in low or "how were you built" in low or "how you were built" in low:
            return self._action("self_explain", {"query": t})

        if low in ("open aurora", "show aurora"):
            return self._action("open_aurora", {"target": "aurora"})
        if low in ("open workspace", "show workspace"):
            return self._action("open_workspace", {"target": "workspace"})
        if low in ("open agent works", "open agent", "agent works"):
            return self._action("open_agent_works", {"target": "agent"})

        if low.startswith("allow workspace root "):
            root = t[len("allow workspace root "):].strip()
            return self._action("allow_workspace_root", {"root": root})

        create = re.match(r"^create file\s+([^\s]+)(?:\s+with\s+(.+))?$", t, flags=re.IGNORECASE)
        if create:
            return self._action("create_file", {"path": create.group(1), "content": create.group(2) or ""})

        edit = re.match(r"^edit file\s+([^\s]+)\s+with\s+(.+)$", t, flags=re.IGNORECASE)
        if edit:
            return self._action("edit_file", {"path": edit.group(1), "content": edit.group(2)})

        summarize_file = re.match(r"^summarize file\s+([^\s]+)$", t, flags=re.IGNORECASE)
        if summarize_file:
            return self._action("summarize_file", {"path": summarize_file.group(1)})

        list_files = re.match(r"^list workspace files(?:\s+depth\s+(\d+))?$", t, flags=re.IGNORECASE)
        if list_files:
            return self._action("list_workspace_files", {"depth": int(list_files.group(1) or 2)})

        if low.startswith("switch to "):
            raw = low.replace("switch to ", "", 1).replace(" mode", "").strip()
            alias = {"drawing": "study", "pdf": "research", "pdf/office": "research", "office": "research", "coding": "coding"}
            mapped = alias.get(raw, raw)
            return self._action("set_mode", {"mode": mapped, "requested_mode": raw})

        for mode in ["study", "coding", "exam", "calm", "deep_work", "meeting"]:
            if low == mode or f"{mode} mode" in low or low.startswith(f"set {mode}"):
                return self._action("set_mode", {"mode": mode})

        if "save session" in low or "store session" in low:
            return self._action("save_session", {})
        if "continue last session" in low or "resume session" in low or "continue session" in low:
            return self._action("resume_session", {})

        if "stop focus" in low or "cancel focus" in low or low == "stop timer" or low == "cancel timer":
            return self._action("stop_focus_timer", {})
        if low.startswith("focus"):
            minutes = self._extract_int(low) or 25
            return self._action("start_focus_timer", {"minutes": minutes})

        if low.startswith("summarize"):
            return self._action("summarize_text", {"text": t})

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
