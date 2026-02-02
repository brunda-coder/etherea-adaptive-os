from __future__ import annotations

import asyncio
import threading
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QApplication

# --- Etherea Core Agentic Architecture ---
from corund.policy_engine import policy_engine
from corund.system_tools import register_system_tools
from corund.tool_router import tool_router
from corund.state import get_state
# --- End Etherea Core ---

from corund.app_runtime import user_data_dir
from corund.ei_engine import EIEngine
from corund.ui.main_window_v3 import EthereaMainWindowV3
from corund.signals import signals
from corund.workspace_manager import WorkspaceManager
from corund.workspace_registry import WorkspaceRegistry, WorkspaceType, WorkspaceRecord
from corund.workspace_ai.workspace_controller import WorkspaceController
from corund.aurora_actions import ActionRegistry
from corund.aurora_state import AuroraStateStore
from corund.aurora_pipeline import AuroraDecisionPipeline
from corund.os_adapter import OSAdapter
from corund.os_pipeline import OSPipeline

if TYPE_CHECKING:
    from corund.voice_engine import VoiceEngine

from corund.voice_engine import get_voice_engine


class AppController(QObject):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self._log_path = Path(user_data_dir()) / "etherea.log"

        # --- Agentic Core Threading ---
        self._async_loop: asyncio.AbstractEventLoop | None = None
        self._async_thread: threading.Thread | None = None
        self._loop_started = threading.Event()
        # --- End Agentic Core ---

        # Core Components
        self.ei_engine = EIEngine()
        self.workspace_manager = WorkspaceManager()
        self.workspace_registry = WorkspaceRegistry()
        self.ws_controller = WorkspaceController(self.workspace_manager)
        self.action_registry = ActionRegistry.default()
        self.aurora_state_store = AuroraStateStore(self.action_registry)
        self.os_pipeline = OSPipeline(OSAdapter(dry_run=False))
        self.aurora_pipeline = AuroraDecisionPipeline(
            registry=self.action_registry,
            workspace_registry=self.workspace_registry,
            workspace_manager=self.workspace_manager,
            state_store=self.aurora_state_store,
            os_pipeline=self.os_pipeline,
            log_cb=self.log,
        )
        self.voice_engine: Optional["VoiceEngine"] = None

        # UI
        self.window = EthereaMainWindowV3(self)

        self._connect_signals()

        self._heartbeat = QTimer(self)
        self._heartbeat.setInterval(250)
        self._heartbeat.timeout.connect(self._tick)

    def _connect_signals(self) -> None:
        signals.emotion_updated.connect(self.window.on_emotion_updated)
        signals.system_log.connect(self.window.log_ui)
        signals.system_log.connect(self._write_log)
        signals.proactive_trigger.connect(self.on_proactive_trigger)
        signals.workspace_changed.connect(self.window.on_workspace_changed)

    def _tick(self) -> None:
        # Sync aurora state with the UI
        current_workspace = self.workspace_registry.get_current()
        emotion_tag = getattr(self.window.avatar, "emotion_tag", "calm")
        self.aurora_state_store.update(
            workspace_id=current_workspace.workspace_id if current_workspace else None,
            workspace_name=current_workspace.name if current_workspace else None,
            session_active=current_workspace is not None,
            last_saved=current_workspace.last_saved if current_workspace else None,
            emotion_tag=emotion_tag,
            focus=self.ei_engine.state.get("focus", 0.5),
            stress=self.ei_engine.state.get("stress", 0.2),
            energy=self.ei_engine.state.get("energy", 0.5),
        )
    
    def _run_async_loop(self):
        """Runs the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(asyncio.new_event_loop())
        self._async_loop = asyncio.get_running_loop()
        self._loop_started.set() # Signal that the loop is ready
        self._async_loop.run_forever()
        # Clean up after loop stops
        self._async_loop.close()
        self._async_loop = None
        self.log("Asyncio event loop stopped.")

    def _initialize_agentic_core(self):
        """Initializes and starts the agentic components."""
        self.log("🚀 Initializing Etherea's agentic core...")
        
        self._async_thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self._async_thread.start()
        
        if not self._loop_started.wait(timeout=5):
            self.log("❌ CRITICAL: Asyncio event loop failed to start.")
            return

        self.log("Registering system tools...")
        register_system_tools()
        
        self._async_loop.call_soon_threadsafe(policy_engine.start)
        self.log("✅ Agentic core is alive.")

    def start(self) -> None:
        self.ei_engine.start()
        self._heartbeat.start()
        self.log("✅ EI Engine started.")

        self._initialize_agentic_core()

        # Set the initial workspace in the global state
        initial_workspace = self.workspace_registry.get_current()
        if initial_workspace:
            self.switch_workspace(initial_workspace.name)

        try:
            self.voice_engine = get_voice_engine()
            if self.voice_engine and getattr(self.voice_engine, "has_mic", False):
                self.voice_engine.start_command_loop()
                self.log("✅ Voice engine started.")
            else:
                self.log("🔇 Voice engine unavailable (no mic or missing deps).")
        except Exception as exc:
            self.log(f"⚠️ Voice engine init failed: {exc}")

        self.window.show()

    def shutdown(self) -> None:
        self._heartbeat.stop()
        self.ei_engine.stop()
        self.log("🔌 Shutting down agentic core...")
        if self._async_loop and self._async_thread and self._async_thread.is_alive():
            self._async_loop.call_soon_threadsafe(policy_engine.stop)
            self._async_loop.call_soon_threadsafe(self._async_loop.stop)
            self._async_thread.join(timeout=2)
        self.log("✅ Shutdown complete.")

    def get_available_workspaces(self) -> list[WorkspaceRecord]:
        """Returns the list of all core workspaces."""
        return self.workspace_registry.list_workspaces()

    def switch_workspace(self, workspace_name: WorkspaceType) -> None:
        """
        Switches the application to a new workspace and updates the global state.
        """
        self.log(f"Switching to workspace: {workspace_name}")
        new_workspace = self.workspace_registry.switch_workspace(workspace_name)
        if not new_workspace:
            self.log(f"❌ Failed to switch to workspace: {workspace_name}")
            return

        # Update the global EthereaState
        if self._async_loop:
            state = get_state()
            coro = state.set_current_workspace(new_workspace.name, source="AppController")
            future = asyncio.run_coroutine_threadsafe(coro, self._async_loop)
            try:
                future.result(timeout=1)
            except Exception as e:
                self.log(f"❌ Error updating global state for workspace change: {e}")

        signals.workspace_changed.emit(new_workspace.name)
        self.log(f"✅ Switched to workspace: {new_workspace.name}")

    def execute_user_command(self, cmd: str, source: str = "ui") -> None:
        cmd = (cmd or "").strip()
        if not cmd:
            return

        self.log(f"⚡ CMD[{source}]: {cmd}")

        if self._handle_avatar_commands(cmd):
            return

        try:
            out = self.ws_controller.handle_command(cmd, source=source)
            self.log(f"✅ OUT: {out}")
        except Exception as e:
            self.log(f"❌ command failed: {e}")

    def on_proactive_trigger(self, trigger_type: str) -> None:
        self.log(f"🧠 Proactive trigger: {trigger_type}")

    def _handle_avatar_commands(self, cmd: str) -> bool:
        return False

    def _write_log(self, message: str) -> None:
        try:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            if not self._log_path.exists():
                self._log_path.touch()
            with self._log_path.open("a", encoding="utf-8") as f:
                f.write(message + "\n")
        except Exception:
            pass

    def log(self, message: str) -> None:
        signals.system_log.emit(message)