from __future__ import annotations

from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from corund.ui.aurora_bar import AuroraBar
from corund.ui.avatar_panel import AvatarPanel
from corund.ui.candy_toast import CandyToastManager
from corund.ui.demo_mode_panel import DemoModePanel
from corund.ui.ethera_dock import EtheraDock
from corund.ui.ethera_command_bar import EthereaCommandBar
from corund.ui.focus_canvas import FocusCanvas
from corund.ui.settings_privacy_widget import SettingsPrivacyWidget
from corund.ui.status_ribbon import StatusRibbon
from corund.ui.theme import get_theme_manager
from corund.workspace_behaviors import WORKSPACE_BEHAVIORS
from corund.tutorial_overlay import TutorialOverlayStateMachine
from corund.ui.tutorial_coach_overlay import TutorialCoachOverlay
from corund.ui.workspace_hub import WorkspaceHubWidget
from core.emotion import UserState
from corund.notifications import NotificationManager


class EthereaMainWindowV3(QMainWindow):
    def __init__(self, app_controller) -> None:
        super().__init__()
        self.app_controller = app_controller
        self.setWindowTitle("Etherea OS")
        self.resize(1280, 780)

        root = QWidget()
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        self.aurora_bar = AuroraBar()
        self.aurora_bar.search.returnPressed.connect(lambda: self.execute_user_command(self.aurora_bar.search.text()))
        main_layout.addWidget(self.aurora_bar)

        self.boot_health_hud = QFrame()
        self.boot_health_hud.setProperty("panel", True)
        hud_layout = QHBoxLayout(self.boot_health_hud)
        hud_layout.setContentsMargins(10, 6, 10, 6)
        hud_layout.setSpacing(12)
        self.hud_avatar = QLabel("Avatar: --")
        self.hud_assets = QLabel("Assets: --")
        self.hud_audio = QLabel("Audio/TTS: --")
        self.hud_brain = QLabel("Brain: OFFLINE")
        self.hud_sensors = QLabel("Sensors: OFF")
        for w in (self.hud_avatar, self.hud_assets, self.hud_audio, self.hud_brain, self.hud_sensors):
            hud_layout.addWidget(w)
        hud_layout.addStretch(1)
        main_layout.addWidget(self.boot_health_hud)

        mid_row = QHBoxLayout()
        mid_row.setSpacing(12)

        self.avatar_panel = AvatarPanel()
        mid_row.addWidget(self.avatar_panel, 1)

        center_col = QVBoxLayout()
        center_col.setSpacing(12)

        self.workspace_selector = QComboBox()
        self.populate_workspaces()
        self.workspace_selector.currentTextChanged.connect(self.on_workspace_selected)
        center_col.addWidget(self.workspace_selector)

        self.center_stack = QStackedWidget()
        self.focus_canvas = FocusCanvas()
        self.workspace_hub = WorkspaceHubWidget(self.app_controller)
        self.settings_panel = SettingsPrivacyWidget()
        self.settings_panel.avatar_settings_changed.connect(self._apply_avatar_settings)
        self.settings_panel.emotion_settings_changed.connect(self._apply_emotion_settings)
        self.settings_panel.voice_settings_changed.connect(self._apply_voice_settings)
        self.demo_panel = DemoModePanel()
        self.center_stack.addWidget(self.focus_canvas)
        self.center_stack.addWidget(self.workspace_hub)
        self.center_stack.addWidget(self.settings_panel)
        self.center_stack.addWidget(self.demo_panel)
        center_col.addWidget(self.center_stack, 3)

        mid_row.addLayout(center_col, 2)

        self.ethera_dock = EtheraDock()
        self.ethera_dock.command_palette.submitted.connect(self.execute_user_command)
        mid_row.addWidget(self.ethera_dock, 1)
        main_layout.addLayout(mid_row, 1)

        self.status_ribbon = StatusRibbon()
        main_layout.addWidget(self.status_ribbon)

        self.toast_manager = CandyToastManager(self)
        self.tutorial_overlay = TutorialOverlayStateMachine()
        self.tutorial_coach = TutorialCoachOverlay(self)
        self.tutorial_coach.setGeometry(100, 100, 480, 180)
        self.home_command_input = EthereaCommandBar(self, app_controller=self.app_controller)
        self.home_command_input.returnPressed.connect(lambda: self.execute_user_command(self.home_command_input.text()))
        self.ethera_dock.layout().insertWidget(0, self.home_command_input)

        self._bind_shortcuts()
        get_theme_manager().theme_changed.connect(self._on_theme_changed)
        self._apply_accessibility_mode()
        self._show_boot_sequence()

        QTimer.singleShot(900, lambda: self.app_controller.tts_engine.speak("I can open a workspace, run a command, or summarize notes. Want a quick tour?", {"source": "onboarding"}))

    def set_boot_health(self, status: dict) -> None:
        avatar = status.get("avatar", {})
        assets = status.get("assets", {})
        audio = status.get("audio_tts", {})
        brain = status.get("brain", {})
        sensors = status.get("sensors", {})
        self.hud_avatar.setText(f"Avatar: {'OK' if avatar.get('ok') else 'FAIL'} ({avatar.get('reason', '-')})")
        self.hud_assets.setText(f"Assets: {'OK' if assets.get('ok') else 'FAIL'} ({assets.get('reason', '-')})")
        self.hud_audio.setText(f"Audio/TTS: {'OK' if audio.get('ok') else 'FAIL'} ({audio.get('reason', '-')})")
        self.hud_brain.setText(f"Brain: {brain.get('mode', 'OFFLINE').upper()}")
        self.hud_sensors.setText(f"Sensors: {'ON' if sensors.get('enabled') else 'OFF'}")

    def _bind_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+K"), self, activated=self._focus_command)
        QShortcut(QKeySequence("Esc"), self, activated=self._handle_escape_kill_switch)
        QShortcut(QKeySequence("Ctrl+1"), self, activated=lambda: self.center_stack.setCurrentWidget(self.focus_canvas))
        QShortcut(QKeySequence("Ctrl+2"), self, activated=lambda: self.center_stack.setCurrentWidget(self.settings_panel))
        QShortcut(QKeySequence("Ctrl+3"), self, activated=lambda: self.center_stack.setCurrentWidget(self.demo_panel))
        QShortcut(QKeySequence("Ctrl+Shift+M"), self, activated=self._toggle_reduced_motion)

    def populate_workspaces(self):
        workspaces = self.app_controller.get_available_workspaces()
        current_workspace = self.app_controller.workspace_registry.get_current()
        for ws in workspaces:
            self.workspace_selector.addItem(ws.name)
        if current_workspace:
            self.workspace_selector.setCurrentText(current_workspace.name)

    @Slot(str)
    def on_workspace_selected(self, workspace_name: str):
        if self.app_controller.workspace_registry.get_current() and self.app_controller.workspace_registry.get_current().name != workspace_name:
            self.app_controller.switch_workspace(workspace_name)
        self.center_stack.setCurrentWidget(self.workspace_hub)
        self.workspace_hub.set_mode(workspace_name)

    @Slot(str)
    def on_workspace_changed(self, workspace_name: str):
        if self.workspace_selector.currentText() != workspace_name:
            self.workspace_selector.setCurrentText(workspace_name)
        self.status_ribbon.workspace_mode.setText(f"Workspace · {workspace_name}")
        self._apply_workspace_ui_behavior(workspace_name)

    @Slot(str)
    def execute_user_command(self, cmd: str):
        self.app_controller.execute_user_command(cmd, source="ui")

    @Slot(str)
    def log_ui(self, msg: str):
        self.ethera_dock.intent_card.setToolTip(msg)

    @Slot(dict)
    def on_emotion_updated(self, vec: dict):
        f, s, e = vec.get("focus"), vec.get("stress"), vec.get("energy")
        if isinstance(f, (int, float)):
            self.status_ribbon.focus_timer.setText(f"Focus · {float(f):.2f}")
        if isinstance(s, (int, float)) and s > 0.6:
            self.aurora_bar.status.setText("Aurora · Stress")
        if isinstance(e, (int, float)) and e < 0.3:
            self.aurora_bar.status.setText("Aurora · Low Energy")
        self.avatar_panel.update_ei(vec)

    def _apply_workspace_ui_behavior(self, workspace_name: str):
        behavior = WORKSPACE_BEHAVIORS.get(workspace_name)
        if not behavior:
            return
        ui_density = behavior.get("ui_density", "standard")
        is_minimal = ui_density == "minimal"
        self.ethera_dock.setVisible(not is_minimal)
        self.avatar_panel.setVisible(not is_minimal)

    def _show_boot_sequence(self) -> None:
        self.aurora_bar.status.setText("Aurora · Booting")
        QTimer.singleShot(200, lambda: self.avatar_panel.dialogue.setText("“Welcome to Etherea. I’ll guide you.”"))
        QTimer.singleShot(550, self.start_tutorial_overlay)

    def start_tutorial_overlay(self) -> None:
        step = self.tutorial_overlay.start()
        self.aurora_bar.status.setText("Aurora · Tutorial")
        self.avatar_panel.dialogue.setText(f"{step.title}: {step.instruction}")
        self.tutorial_coach.start()

    def _handle_escape_kill_switch(self) -> None:
        self._close_overlays()
        if hasattr(self.app_controller, "emergency_pause_all"):
            self.app_controller.emergency_pause_all()

    def _focus_command(self) -> None:
        self.ethera_dock.command_palette.input.setFocus()

    def _close_overlays(self) -> None:
        self.center_stack.setCurrentWidget(self.focus_canvas)

    def _toggle_reduced_motion(self) -> None:
        theme = get_theme_manager()
        theme.set_accessibility(reduced_motion=not theme.reduced_motion)

    def _on_theme_changed(self) -> None:
        if self.app_controller.app is not None:
            get_theme_manager().apply_to(self.app_controller.app)
        if get_theme_manager().theme_name == "candy":
            self.toast_manager.show_toast("Candy mode activated ✨")
        self._apply_accessibility_mode()
        self.update()

    def _apply_accessibility_mode(self) -> None:
        minimal = get_theme_manager().minimal_mode
        self.ethera_dock.setVisible(not minimal)
        self.avatar_panel.setVisible(not minimal)

    def on_user_state_updated(self, user_state: UserState) -> None:
        confidence = user_state.confidence
        probabilities = user_state.probabilities or {}
        frustrated = probabilities.get("frustrated", 0.0)
        if confidence < 0.35:
            self.avatar_panel.dialogue.setText("“I’m not fully sure how you’re feeling. Want a gentle check-in?”")
            return
        if frustrated > 0.7 and confidence > 0.6:
            self.avatar_panel.dialogue.setText("“Feeling a bit tense? I can simplify the UI and offer a reset.”")
            get_theme_manager().set_accessibility(reduced_motion=True, quiet_mode=True)
            self.ethera_dock.setVisible(False)
        else:
            self.ethera_dock.setVisible(True)

    def _apply_avatar_settings(self, settings: dict) -> None:
        self.avatar_panel.apply_avatar_settings(settings)

    def _apply_emotion_settings(self, settings: dict) -> None:
        engine = self.app_controller.emotion_engine
        if "enabled" in settings:
            engine.set_enabled(settings["enabled"])
        if "camera_opt_in" in settings:
            engine.set_camera_opt_in(settings["camera_opt_in"])
        if settings.get("delete_data"):
            engine.delete_data()
        if settings.get("kill_switch"):
            engine.set_kill_switch(True)

    def _apply_voice_settings(self, settings: dict) -> None:
        tts = self.app_controller.tts_engine
        if "enabled" in settings:
            tts.set_enabled(settings["enabled"])
        if "dramatic_mode" in settings:
            tts.set_dramatic_mode(settings["dramatic_mode"])
            self.avatar_panel.world.set_dramatic_mode(settings["dramatic_mode"])
        self.app_controller.voice_manager.configure(
            voice_enabled=settings.get("enabled"),
            mic_enabled=settings.get("mic_enabled"),
            sensitivity=settings.get("sensitivity"),
        )
        if "call_me_back" in settings:
            NotificationManager.instance().set_call_me_back(settings["call_me_back"])
        if settings.get("speak_demo"):
            self.app_controller.voice_manager.speak_demo()
