from __future__ import annotations

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QFrame,
    QComboBox,
)
from PySide6.QtCore import Slot

from corund.ui.command_palette import CommandPalette
from corund.ui.avatar_heroine_widget import AvatarHeroineWidget
from corund.ui.aurora_canvas_widget import AuroraCanvasWidget
from corund.workspace_registry import WorkspaceType
from corund.workspace_behaviors import WORKSPACE_BEHAVIORS, UIDensity


class EthereaMainWindowV3(QMainWindow):
    def __init__(self, app_controller) -> None:
        super().__init__()
        self.app_controller = app_controller
        self.setWindowTitle("Etherea OS")
        self.resize(1200, 720)

        root = QWidget()
        self.setCentralWidget(root)

        main_layout = QHBoxLayout(root)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        # Left side: Workspace, Command and Avatar
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)

        self.workspace_selector = QComboBox()
        self.workspace_selector.setStyleSheet(
            "QComboBox { background-color: #1a1b26; color: white; border-radius: 8px; padding: 8px; }"
        )
        self.populate_workspaces()
        self.workspace_selector.currentTextChanged.connect(self.on_workspace_selected)
        left_layout.addWidget(self.workspace_selector)

        self.command_palette = CommandPalette()
        self.command_palette.submitted.connect(self.execute_user_command)
        left_layout.addWidget(self.command_palette)

        self.avatar = AvatarHeroineWidget()
        self.avatar.setStyleSheet(
            "QWidget { background: #0b0b12; border-radius: 18px; }"
        )
        left_layout.addWidget(self.avatar, 1)

        main_layout.addLayout(left_layout, 1)

        # Right side: Aurora, Console, and Status
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        self.title = QLabel("Etherea Console")
        self.title.setStyleSheet("font-size:18px; font-weight:700; color:white;")
        right_layout.addWidget(self.title)

        self.aurora_canvas = AuroraCanvasWidget()
        right_layout.addWidget(self.aurora_canvas)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet(
            "QTextEdit { background:#11121a; color:#e8e8ff; border:1px solid #22243a;"
            "border-radius:14px; padding:10px; font-family:monospace; font-size:13px; }"
        )
        right_layout.addWidget(self.console, 1)

        self.status_frame = QFrame()
        self.status_frame.setStyleSheet(
            "QFrame { background:#101018; border:1px solid #1f2135; border-radius:16px; padding:10px; }"
            "QLabel { color:#dcdcff; font-size:13px; }"
        )
        status_layout = QVBoxLayout(self.status_frame)

        self.l_mode = QLabel("Workspace: --")
        self.l_focus = QLabel("Focus: --")
        self.l_stress = QLabel("Stress: --")
        self.l_energy = QLabel("Energy: --")
        self.l_timer = QLabel("Focus timer: --")

        status_layout.addWidget(self.l_mode)
        status_layout.addWidget(self.l_timer)
        status_layout.addWidget(self.l_focus)
        status_layout.addWidget(self.l_stress)
        status_layout.addWidget(self.l_energy)
        right_layout.addWidget(self.status_frame)

        main_layout.addLayout(right_layout, 2)

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
        self.l_mode.setText(f"Workspace: {workspace_name}")
        if self.workspace_selector.currentText() != workspace_name:
            self.workspace_selector.setCurrentText(workspace_name)
        self._apply_workspace_ui_behavior(workspace_name)

    @Slot(str)
    def execute_user_command(self, cmd: str):
        self.app_controller.execute_user_command(cmd, source="ui")

    @Slot(str)
    def log_ui(self, msg: str):
        self.console.append(msg)

    @Slot(dict)
    def on_emotion_updated(self, vec: dict):
        f = vec.get("focus")
        s = vec.get("stress")
        e = vec.get("energy")

        if isinstance(f, (int, float)):
            self.l_focus.setText(f"Focus: {float(f):.2f}")
        if isinstance(s, (int, float)):
            self.l_stress.setText(f"Stress: {float(s):.2f}")
        if isinstance(e, (int, float)):
            self.l_energy.setText(f"Energy: {float(e):.2f}")

        self.avatar.update_ei(vec)

    def _apply_workspace_ui_behavior(self, workspace_name: str):
        """Adjusts the UI's density and components based on the workspace behavior."""
        behavior = WORKSPACE_BEHAVIORS.get(workspace_name)
        if not behavior:
            return

        self.l_mode.setText(f"Workspace: {workspace_name}")
        self.avatar.set_mode_persona(workspace_name)

        ui_density = behavior.get("ui_density", "standard")

        if ui_density == "minimal":
            self.aurora_canvas.setVisible(False)
            self.console.setVisible(False)
            self.status_frame.setVisible(False)
            self.title.setVisible(False)
        elif ui_density == "dense":
            self.aurora_canvas.setVisible(True)
            self.console.setVisible(True)
            self.status_frame.setVisible(True)
            self.title.setVisible(True)
        else: # Standard
            self.aurora_canvas.setVisible(True)
            self.console.setVisible(True)
            self.status_frame.setVisible(True)
            self.title.setVisible(True)
