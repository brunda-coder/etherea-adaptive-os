from __future__ import annotations

import asyncio
import threading
import time
from pathlib import Path
from typing import Optional, TYPE_CHECKING

import os

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QApplication

from corund.state import get_state

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
from corund.resource_manager import ResourceManager
from corund.runtime_diagnostics import RuntimeDiagnostics
from corund.perf import get_startup_timer, log_startup_report

if TYPE_CHECKING:
    from corund.voice_engine import VoiceEngine


class AppController(QObject):
    def __init__(
        self,
        app: QApplication | None = None,
        *,
        safe_mode: bool = False,
        diagnostics: RuntimeDiagnostics | None = None,
    ) -> None:
        super().__init__()
        self.app = app
        self.safe_mode = safe_mode
        self.diagnostics = diagnostics
        self._log_path = ResourceManager.logs_dir() / "etherea.log"

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
        self._agentic_timer: QTimer | None = None
        self._agentic_started_at: float | None = None
        self._profile_logged = False

        # UI
        self.window = EthereaMainWindowV3(self)

        self._connect_signals()

        self._heartbeat = QTimer(self)
        self._heartbeat.setInterval(250)
        self._heartbeat.timeout.connect(self._tick)

    def initialize(self) -> None:
        """Initializes UI theming and starts core services."""
        from corund.ui.theme import get_theme_manager

        if self.app is not None:
            get_theme_manager().apply_to(self.app)
        self.start()

    def _connect_signals(self) -> None:
        signals.emotion_updated.connect(self.window.on_emotion_updated)
        signals.system_log.connect(self.window.log_ui)
        signals.system_log.connect(self._write_log)
        signals.proactive_trigger.connect(self.on_proactive_trigger)
        signals.workspace_changed.connect(self.window.on_workspace_changed)

    def _tick(self) -> None:
        # Sync aurora state with the UI
        current_workspace = self.workspace_registry.get_current()
        emotion_tag = getattr(self.window.avatar_panel, "emotion_tag", "calm")
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
        self._agentic_started_at = time.monotonic()

        if self._agentic_timer is None:
            self._agentic_timer = QTimer(self)
            self._agentic_timer.setInterval(50)
            self._agentic_timer.timeout.connect(self._poll_agentic_ready)
        self._agentic_timer.start()

    def _poll_agentic_ready(self) -> None:
        if self._loop_started.is_set():
            if self._agentic_timer is not None:
                self._agentic_timer.stop()
            try:
                from corund.system_tools import register_system_tools
                from corund.policy_engine import policy_engine

                self.log("Registering system tools...")
                register_system_tools()
                self._async_loop.call_soon_threadsafe(policy_engine.start)
                self.log("✅ Agentic core is alive.")
                get_startup_timer().mark("agentic")
            except Exception as exc:
                self.log(f"⚠️ Agentic core init failed: {exc}")
            return

        if self._agentic_started_at is not None and time.monotonic() - self._agentic_started_at > 5:
            if self._agentic_timer is not None:
                self._agentic_timer.stop()
            self.log("❌ Agentic core init timed out. Running in degraded mode.")

    def start(self) -> None:
        timer = get_startup_timer()
        self.ei_engine.start()
        self._heartbeat.start()
        self.log("✅ EI Engine started.")

        if self.safe_mode:
            self.log("🛟 Safe Mode enabled: skipping agentic core + voice engine.")
            os.environ["ETHEREA_DISABLE_SENSORS"] = "1"
            from corund.ui.theme import get_theme_manager

            get_theme_manager().set_accessibility(reduced_motion=True, minimal_mode=True, quiet_mode=True)
        else:
            QTimer.singleShot(0, self._init_agentic_deferred)
            self._initialize_agentic_core()

        # Set the initial workspace in the global state
        initial_workspace = self.workspace_registry.get_current()
        if initial_workspace:
            self.switch_workspace(initial_workspace.name)

        self.window.show()
        timer.mark("ui")

        if not self.safe_mode:
            QTimer.singleShot(800, self._init_voice_deferred)
        else:
            self._log_startup_profile()

    def _init_agentic_deferred(self) -> None:
        try:
            self._initialize_agentic_core()
        except Exception as exc:
            self.log(f"⚠️ Agentic core init failed: {exc}")

    def _init_voice_deferred(self) -> None:
        try:
            from corund.voice_engine import get_voice_engine

            self.voice_engine = get_voice_engine()
            if self.voice_engine and getattr(self.voice_engine, "has_mic", False):
                self.voice_engine.start_command_loop()
                self.log("✅ Voice engine started.")
            else:
                self.log("🔇 Voice engine unavailable (no mic or missing deps).")
        except Exception as exc:
            self.log(f"⚠️ Voice engine init failed: {exc}")
        get_startup_timer().mark("voice")
        self._log_startup_profile()
        if not self.safe_mode:
            try:
                self.voice_engine = get_voice_engine()
                if self.voice_engine and getattr(self.voice_engine, "has_mic", False):
                    self.voice_engine.start_command_loop()
                    self.log("✅ Voice engine started.")
                else:
                    self.log("🔇 Voice engine unavailable (no mic or missing deps).")
            except Exception as exc:
                self.log(f"⚠️ Voice engine init failed: {exc}")

    def _log_startup_profile(self) -> None:
        if self._profile_logged:
            return
        report = get_startup_timer().report()
        if report:
            log_startup_report(report)
            self._profile_logged = True

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
        normalized = cmd.lower()
        if normalized in {"demo mode", "start demo", "start demo mode", "demo start", "guided tour"}:
            self.window.start_demo_mode()
            self.log("🎬 Demo mode started.")
            return True
        if normalized in {"stop demo", "stop demo mode", "end demo", "end demo mode", "exit demo"}:
            self.window.stop_demo_mode()
            self.log("🛑 Demo mode ended.")
            return True
        if normalized in {"demo next", "next demo", "next step", "tour next"}:
            self.window.next_demo_step()
            self.log("➡️ Demo step advanced.")
            return True
        if normalized in {"demo back", "demo prev", "previous step", "tour back"}:
            self.window.prev_demo_step()
            self.log("⬅️ Demo step reversed.")
            return True
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
