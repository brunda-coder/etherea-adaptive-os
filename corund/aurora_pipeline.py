from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from corund.aurora_actions import ActionRegistry, ActionSpec
from corund.aurora_state import AuroraStateStore
from corund.event_model import Event, create_event
from corund.event_bus import EventBus, event_bus
from corund.workspace_manager import WorkspaceManager
from corund.workspace_registry import WorkspaceRegistry
from corund.os_pipeline import OSPipeline
from corund.workspace_manager import WorkspaceManager
from corund.workspace_registry import WorkspaceRegistry


@dataclass(frozen=True)
class AuroraEvent:
    event_type: str
    payload: Dict[str, object]


class AuroraDecisionPipeline:
    def __init__(
        self,
        registry: ActionRegistry,
        workspace_registry: WorkspaceRegistry,
        workspace_manager: WorkspaceManager,
        state_store: AuroraStateStore,
        os_pipeline: Optional[OSPipeline] = None,
        bus: Optional[EventBus] = None,
        log_cb: Optional[Callable[[str], None]] = None,
    ):
        self._registry = registry
        self._workspace_registry = workspace_registry
        self._workspace_manager = workspace_manager
        self._state_store = state_store
        self._listeners: List[Callable[[Event], None]] = []
        self._bus = bus or event_bus
        self._os_pipeline = os_pipeline
        self._log_cb = log_cb

    def subscribe(self, listener: Callable[[Event], None]) -> None:
        self._listeners.append(listener)

    def _emit(self, event_type: str, payload: Dict[str, object]) -> None:
        event = create_event(
            event_type,
            source="aurora_pipeline",
            payload=payload,
            priority=40,
            privacy_level="normal",
        )
        self._bus.emit(event)
        self._listeners: List[Callable[[AuroraEvent], None]] = []
        self._log_cb = log_cb

    def subscribe(self, listener: Callable[[AuroraEvent], None]) -> None:
        self._listeners.append(listener)

    def _emit(self, event_type: str, payload: Dict[str, object]) -> None:
        event = AuroraEvent(event_type=event_type, payload=payload)
        for listener in self._listeners:
            listener(event)

    def _log(self, message: str) -> None:
        if self._log_cb:
            self._log_cb(message)

    def handle_intent(self, intent_or_action: str) -> Dict[str, object]:
        action = self._registry.get(intent_or_action)
        if action is None:
            action = self._registry.action_for_intent(intent_or_action)
        if action is None:
            self._emit("ACTION_BLOCKED", {"reason": "unknown_intent", "intent": intent_or_action})
            return {"ok": False, "action": "unknown", "intent": intent_or_action}

        runtime = self._state_store.runtime
        if runtime.dnd_active and action.dnd_blocked:
            self._emit("ACTION_BLOCKED", {"reason": "dnd", "intent": action.intent})
            self._log(f"⛔ DND blocked action: {action.label}")
            return {"ok": False, "action": "blocked", "intent": action.intent}

        self._emit("ACTION_STARTED", {"intent": action.intent})
        result = self._dispatch_action(action)
        self._emit("ACTION_FINISHED", {"intent": action.intent})
        self._emit("STATE_UPDATED", {"mode": self._state_store.runtime.current_mode})
        return result

    def _dispatch_action(self, action: ActionSpec) -> Dict[str, object]:
        handler_map = {
            "set_mode_idle": self._set_mode_idle,
            "set_mode_focus": self._set_mode_focus,
            "set_mode_break": self._set_mode_break,
            "workspace_create": self._workspace_create,
            "workspace_resume": self._workspace_resume,
            "workspace_save_snapshot": self._workspace_save_snapshot,
            "toggle_dnd_on": self._toggle_dnd_on,
            "toggle_dnd_off": self._toggle_dnd_off,
            "os_open_workspace_folder": self._os_open_workspace_folder,
        }
        handler = handler_map.get(action.intent)
        if handler is None:
            self._emit("ACTION_BLOCKED", {"reason": "no_handler", "intent": action.intent})
            return {"ok": False, "action": "unknown", "intent": action.intent}
        return handler()

    def _set_mode_idle(self) -> Dict[str, object]:
        self._state_store.update(current_mode="idle")
        self._log("🌌 Aurora mode → idle")
        return {"ok": True, "action": "set_mode", "mode": "idle"}

    def _set_mode_focus(self) -> Dict[str, object]:
        self._state_store.update(current_mode="focus")
        self._log("🎯 Aurora mode → focus")
        return {"ok": True, "action": "set_mode", "mode": "focus"}

    def _set_mode_break(self) -> Dict[str, object]:
        self._state_store.update(current_mode="break")
        self._log("🌿 Aurora mode → break")
        return {"ok": True, "action": "set_mode", "mode": "break"}

    def _workspace_create(self) -> Dict[str, object]:
        record = self._workspace_registry.create_workspace()
        self._state_store.update(
            workspace_id=record.workspace_id,
            workspace_name=record.name,
            session_active=True,
            last_saved=record.last_saved,
        )
        self._log(f"🗂️ Workspace created → {record.name}")
        return {"ok": True, "action": "workspace_create", "workspace": record.workspace_id}

    def _workspace_resume(self) -> Dict[str, object]:
        record = self._workspace_registry.resume_last()
        if not record:
            self._log("⚠️ No workspace to resume")
            return {"ok": False, "action": "workspace_resume", "reason": "none"}
        self._state_store.update(
            workspace_id=record.workspace_id,
            workspace_name=record.name,
            session_active=True,
            last_saved=record.last_saved,
        )
        self._log(f"🔄 Workspace resumed → {record.name}")
        return {"ok": True, "action": "workspace_resume", "workspace": record.workspace_id}

    def _workspace_save_snapshot(self) -> Dict[str, object]:
        snapshot_payload = {
            "open_files": list(self._workspace_manager.open_files.keys()),
            "notes": "aurora snapshot",
        }
        path = self._workspace_registry.save_snapshot(snapshot_payload)
        if not path:
            return {"ok": False, "action": "workspace_save_snapshot", "reason": "no_workspace"}
        record = self._workspace_registry.get_current()
        self._state_store.update(
            workspace_id=record.workspace_id if record else None,
            workspace_name=record.name if record else None,
            session_active=record is not None,
            last_saved=record.last_saved if record else None,
        )
        self._log("💾 Workspace snapshot saved")
        return {"ok": True, "action": "workspace_save_snapshot", "path": str(path)}

    def _toggle_dnd_on(self) -> Dict[str, object]:
        self._state_store.update(dnd_active=True)
        self._log("🔕 DND enabled")
        return {"ok": True, "action": "toggle_dnd", "enabled": True}

    def _toggle_dnd_off(self) -> Dict[str, object]:
        self._state_store.update(dnd_active=False)
        self._log("✅ Override cleared")
        return {"ok": True, "action": "toggle_dnd", "enabled": False}

    def _os_open_workspace_folder(self) -> Dict[str, object]:
        current = self._workspace_registry.get_current()
        if not current:
            self._emit("ACTION_BLOCKED", {"reason": "no_workspace", "intent": "os_open_workspace_folder"})
            return {"ok": False, "action": "os_open_workspace_folder", "reason": "no_workspace"}
        if not self._os_pipeline:
            self._emit("ACTION_BLOCKED", {"reason": "no_os_pipeline", "intent": "os_open_workspace_folder"})
            return {"ok": False, "action": "os_open_workspace_folder", "reason": "no_pipeline"}
        return self._os_pipeline.handle_intent(
            "OPEN_FOLDER",
            {"path": current.path, "confirm": True},
            source="aurora_pipeline",
        )
