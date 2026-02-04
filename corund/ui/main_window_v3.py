from __future__ import annotations

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from corund.ui.aurora_bar import AuroraBar
from corund.ui.avatar_panel import AvatarPanel
from corund.ui.demo_mode_panel import DemoModePanel
from corund.ui.ethera_dock import EtheraDock
from corund.ui.focus_canvas import FocusCanvas
from corund.ui.settings_privacy_widget import SettingsPrivacyWidget
from corund.ui.status_ribbon import StatusRibbon
from corund.ui.theme import get_theme_manager
from corund.workspace_behaviors import WORKSPACE_BEHAVIORS
from corund.workspace_registry import WorkspaceType


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
        self.aurora_bar.search.returnPressed.connect(
            lambda: self.execute_user_command(self.aurora_bar.search.text())
        )
        main_layout.addWidget(self.aurora_bar)

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
        self.settings_panel = SettingsPrivacyWidget()
        self.demo_panel = DemoModePanel()
        self.center_stack.addWidget(self.focus_canvas)
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

        self._bind_shortcuts()
        get_theme_manager().theme_changed.connect(self._on_theme_changed)
        self._apply_accessibility_mode()

    def _bind_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+K"), self, activated=self._focus_command)
        QShortcut(QKeySequence("Esc"), self, activated=self._close_overlays)
        QShortcut(QKeySequence("Ctrl+1"), self, activated=lambda: self.center_stack.setCurrentWidget(self.focus_canvas))
        QShortcut(QKeySequence("Ctrl+2"), self, activated=lambda: self.center_stack.setCurrentWidget(self.settings_panel))
        QShortcut(QKeySequence("Ctrl+3"), self, activated=lambda: self.center_stack.setCurrentWidget(self.demo_panel))
        QShortcut(QKeySequence("Ctrl+Shift+D"), self, activated=lambda: self.center_stack.setCurrentWidget(self.demo_panel))
        QShortcut(QKeySequence("Ctrl+Shift+P"), self, activated=lambda: self.center_stack.setCurrentWidget(self.settings_panel))
        QShortcut(QKeySequence("Ctrl+Shift+M"), self, activated=self._toggle_reduced_motion)

    def populate_workspaces(self):
        """Fills the workspace selector with available workspaces."""
        workspaces = self.app_controller.get_available_workspaces()
        current_workspace = self.app_controller.workspace_registry.get_current()
        for ws in workspaces:
            self.workspace_selector.addItem(ws.name)
        if current_workspace:
            self.workspace_selector.setCurrentText(current_workspace.name)

    @Slot(str)
    def on_workspace_selected(self, workspace_name: WorkspaceType):
        """Handles the selection of a new workspace from the dropdown."""
        if workspace_name and self.app_controller.workspace_registry.get_current().name != workspace_name:
            self.app_controller.switch_workspace(workspace_name)

    @Slot(str)
    def on_workspace_changed(self, workspace_name: str):
        """Updates the UI when the workspace changes."""
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
        f = vec.get("focus")
        s = vec.get("stress")
        e = vec.get("energy")

        if isinstance(f, (int, float)):
            self.status_ribbon.focus_timer.setText(f"Focus · {float(f):.2f}")
        if isinstance(s, (int, float)) and s > 0.6:
            self.aurora_bar.status.setText("Aurora · Stress")
        if isinstance(e, (int, float)) and e < 0.3:
            self.aurora_bar.status.setText("Aurora · Low Energy")

        self.avatar_panel.update_ei(vec)

    def _apply_workspace_ui_behavior(self, workspace_name: str):
        """Adjusts the UI's density and components based on the workspace behavior."""
        behavior = WORKSPACE_BEHAVIORS.get(workspace_name)
        if not behavior:
            return

        ui_density = behavior.get("ui_density", "standard")

        if ui_density == "minimal":
            self.ethera_dock.setVisible(False)
            self.avatar_panel.setVisible(False)
        elif ui_density == "dense":
            self.ethera_dock.setVisible(True)
            self.avatar_panel.setVisible(True)
        else:
            self.ethera_dock.setVisible(True)
            self.avatar_panel.setVisible(True)

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
        self._apply_accessibility_mode()
        self.update()

    def _apply_accessibility_mode(self) -> None:
        theme = get_theme_manager()
        if theme.minimal_mode:
            self.ethera_dock.setVisible(False)
            self.avatar_panel.setVisible(False)
        else:
            self.ethera_dock.setVisible(True)
            self.avatar_panel.setVisible(True)
