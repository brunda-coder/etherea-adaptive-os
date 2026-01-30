from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from corund.app_registry import AppRegistry
from corund.event_bus import EventBus, event_bus
from corund.event_model import create_event
from corund.os_adapter import OSAdapter


@dataclass
class OSOverrides:
    kill_switch: bool = False
    dnd: bool = False
    manual_lock: bool = False
    privacy_mode: bool = False


class OSPipeline:
    def __init__(
        self,
        adapter: OSAdapter,
        registry: Optional[AppRegistry] = None,
        bus: Optional[EventBus] = None,
    ) -> None:
        self._adapter = adapter
        self._registry = registry or AppRegistry()
        self._bus = bus or event_bus

    def handle_intent(
        self,
        intent: str,
        payload: Dict[str, object],
        *,
        overrides: Optional[OSOverrides] = None,
        source: str = "os_pipeline",
    ) -> Dict[str, object]:
        overrides = overrides or OSOverrides()
        self._emit("OS_ACTION_REQUESTED", payload, source=source)

        if overrides.kill_switch or overrides.manual_lock:
            self._emit("OS_ACTION_BLOCKED", {"reason": "overrides", **payload}, source=source)
            return {"ok": False, "intent": intent, "reason": "overrides"}

        if overrides.privacy_mode:
            self._emit("OS_ACTION_BLOCKED", {"reason": "privacy_mode", **payload}, source=source)
            return {"ok": False, "intent": intent, "reason": "privacy_mode"}

        if overrides.dnd and intent in {"OPEN_URL", "LAUNCH_APP"}:
            self._emit("OS_ACTION_BLOCKED", {"reason": "dnd", **payload}, source=source)
            return {"ok": False, "intent": intent, "reason": "dnd"}

        confirm_required = intent in {"OPEN_URL", "LAUNCH_APP", "OPEN_FILE"}
        if confirm_required and not bool(payload.get("confirm", False)):
            self._emit("OS_ACTION_BLOCKED", {"reason": "confirmation_required", **payload}, source=source)
            return {"ok": False, "intent": intent, "reason": "confirmation_required"}

        self._emit("OS_ACTION_STARTED", payload, source=source)
        result = self._dispatch(intent, payload)
        event_type = "OS_ACTION_FINISHED" if result.get("ok") else "OS_ACTION_FAILED"
        self._emit(event_type, {"intent": intent, **result}, source=source)
        return result

    def _dispatch(self, intent: str, payload: Dict[str, object]) -> Dict[str, object]:
        if intent == "OPEN_FILE":
            path = str(payload.get("path", ""))
            result = self._adapter.open_file(path)
            return {"ok": result.ok, "message": result.message, "detail": result.detail}
        if intent == "OPEN_FOLDER":
            path = str(payload.get("path", ""))
            result = self._adapter.open_folder(path)
            return {"ok": result.ok, "message": result.message, "detail": result.detail}
        if intent == "OPEN_URL":
            url = str(payload.get("url", ""))
            result = self._adapter.open_url(url)
            return {"ok": result.ok, "message": result.message, "detail": result.detail}
        if intent == "REVEAL_PATH":
            path = str(payload.get("path", ""))
            result = self._adapter.reveal_in_explorer(path)
            return {"ok": result.ok, "message": result.message, "detail": result.detail}
        if intent == "LAUNCH_APP":
            app_id = str(payload.get("app_id", ""))
            app = self._registry.get(app_id)
            if not app:
                return {"ok": False, "message": "app_not_found", "detail": app_id}
            result = self._adapter.launch_app(app.path, app.args)
            return {"ok": result.ok, "message": result.message, "detail": result.detail}
        return {"ok": False, "message": "unknown_intent", "detail": intent}

    def _emit(self, event_type: str, payload: Dict[str, object], *, source: str) -> None:
        self._bus.emit(
            create_event(
                event_type,
                source=source,
                payload=payload,
                priority=35,
                privacy_level="normal",
            )
        )
