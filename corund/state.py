from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any

from corund.event_bus import event_bus
from corund.event_model import create_event
# Import the single source of truth for workspaces
from corund.workspace_registry import CORE_WORKSPACES

# Derive valid workspaces from the registry to ensure consistency
VALID_WORKSPACES = set(CORE_WORKSPACES.keys())
VALID_ACTIVITY_STATES = {"idle", "active", "flow"}
VALID_PRIVACY_MODES = {"normal", "strict", "private"}

@dataclass
class EthereaState:
    """
    Global singleton state model for Etherea, the single source of truth.
    All state changes must be performed through its methods, which will
    emit corresponding events on the event bus.
    """
    # Core Metrics
    focus_level: float = 0.5
    cognitive_load: float = 0.2
    activity_state: str = "idle" # idle | active | flow

    # Workspace & Context
    current_workspace: str = "Calm"
    open_documents: List[str] = field(default_factory=list)
    open_pdfs: List[str] = field(default_factory=list)
    open_code_projects: List[str] = field(default_factory=list)

    # System & User
    privacy_mode: str = "normal"
    session_start_time: float = field(default_factory=time.time)
    user_preferences: Dict[str, Any] = field(default_factory=dict)

    async def _emit_state_change(self, event_type: str, payload: Dict[str, Any], source: str):
        """Helper to create and emit a state change event."""
        full_event_type = f"state.{event_type}.changed"
        event = create_event(
            event_type=full_event_type,
            source=source,
            payload=payload
        )
        await event_bus.emit(event)

    async def set_focus_level(self, level: float, source: str):
        level = max(0.0, min(1.0, level))
        if abs(self.focus_level - level) > 0.001:
            self.focus_level = level
            await self._emit_state_change("focus_level", {"value": level}, source)

    async def set_cognitive_load(self, load: float, source: str):
        load = max(0.0, min(1.0, load))
        if abs(self.cognitive_load - load) > 0.001:
            self.cognitive_load = load
            await self._emit_state_change("cognitive_load", {"value": load}, source)

    async def set_activity_state(self, state: str, source: str):
        state = state.lower()
        if state in VALID_ACTIVITY_STATES and self.activity_state != state:
            self.activity_state = state
            await self._emit_state_change("activity_state", {"value": state}, source)

    async def set_current_workspace(self, workspace: str, source: str):
        if workspace in VALID_WORKSPACES and self.current_workspace != workspace:
            self.current_workspace = workspace
            await self._emit_state_change("current_workspace", {"value": workspace}, source)
    
    async def set_privacy_mode(self, mode: str, source: str):
        mode = mode.lower()
        if mode in VALID_PRIVACY_MODES and self.privacy_mode != mode:
            self.privacy_mode = mode
            await self._emit_state_change("privacy_mode", {"value": mode}, source)

    # --- Methods for managing open files ---

    async def add_open_document(self, path: str, source: str):
        if path not in self.open_documents:
            self.open_documents.append(path)
            await self._emit_state_change("open_documents", {"action": "add", "path": path}, source)

    async def remove_open_document(self, path: str, source: str):
        if path in self.open_documents:
            self.open_documents.remove(path)
            await self._emit_state_change("open_documents", {"action": "remove", "path": path}, source)
    
    # (Similar methods for PDFs and code projects would follow)

    def get_session_duration(self) -> float:
        return time.time() - self.session_start_time

# --- Singleton Instance ---
# Note: In a real multi-threaded/async application, this initialization
# would need to be handled carefully. For now, this is sufficient.
_state_instance: EthereaState | None = None

def get_state() -> EthereaState:
    """Access the global EthereaState singleton instance."""
    global _state_instance
    if _state_instance is None:
        _state_instance = EthereaState()
    return _state_instance
