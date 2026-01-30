import sys
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFrame, QApplication, QStackedLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

from corund.state import AppState
from corund.ui.ethera_command_bar import EtheraCommandBar
from corund.ui.aurora_canvas_widget import AuroraCanvasWidget
from corund.ui.avatar_heroine_widget import AvatarHeroineWidget
from corund.ui.holo_panel import HoloPanel
from corund.ui.side_dock import SideDock
from corund.ui.workspace_widget import WorkspaceWidget
from corund.ui.notification_tray import NotificationTray
from corund.ui.settings_widget import SettingsWidget

class HeroMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Etherea — Hero Demo")
        self.resize(1280, 800)
        
        # Central Widget & Layout
        container = QWidget()
        self.setCentralWidget(container)
        
        # Main Layout: HBox [SideDock | ContentStack]
        self.main_layout = QHBoxLayout(container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Side Dock (Left)
        self.side_dock = SideDock()
        self.side_dock.mode_requested.connect(self.handle_dock_mode)
        self.main_layout.addWidget(self.side_dock)
        
        # 2. Content Area (Z-Stack)
        self.content_area = QWidget()
        self.content_layout = QStackedLayout(self.content_area)
        self.content_layout.setStackingMode(QStackedLayout.StackAll)
        self.main_layout.addWidget(self.content_area)
        
        # Layer 0: Aurora Canvas (Background)
        self.aurora = AuroraCanvasWidget()
        self.content_layout.addWidget(self.aurora)
        
        # Layer 1: Holographic Panel (Teaching Mode)
        self.holo_panel = HoloPanel()
        self.holo_panel.setVisible(False)
        self.content_layout.addWidget(self.holo_panel)
        
        # Layer 2: Workspace Grid (Productivity Mode)
        self.workspace = WorkspaceWidget()
        self.workspace.setAttribute(Qt.WA_TranslucentBackground) 
        self.workspace.setVisible(False)
        self.content_layout.addWidget(self.workspace)
        
        # Layer 3: Avatar (Overlay)
        self.avatar = AvatarHeroineWidget()
        self.avatar.setVisible(False) 
        self.content_layout.addWidget(self.avatar)
        
        # Layer 5: Notification Tray
        self.notif_tray = NotificationTray()
        self.notif_tray.setVisible(False)
        self.content_layout.addWidget(self.notif_tray)

        # Layer 6: Settings Widget
        self.settings_widget = SettingsWidget()
        self.settings_widget.setVisible(False)
        self.content_layout.addWidget(self.settings_widget)
        
        # Layer 4: UI Controls (Command Bar + Status)
        self.ui_layer = QWidget()
        self.ui_layer.setAttribute(Qt.WA_TranslucentBackground) 
        self.ui_layer.setAttribute(Qt.WA_TransparentForMouseEvents) 
        self.ui_layout = QVBoxLayout(self.ui_layer)
        self.ui_layout.setContentsMargins(30, 20, 30, 20)
        
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        self.status_label = QLabel("HOME")
        self.status_label.setStyleSheet("color: rgba(255, 255, 255, 0.4); font-size: 10px; font-weight: bold; letter-spacing: 2px;")
        top_bar.addWidget(self.status_label)
        self.ui_layout.addLayout(top_bar)
        
        self.ui_layout.addSpacing(20)
        self.ui_layout.setAlignment(Qt.AlignTop)
        
        self.cmd_bar = EtheraCommandBar()
        self.cmd_bar.setFixedWidth(600)
        self.cmd_bar.setVisible(False) 
        self.cmd_bar.returnPressed.connect(self.check_command)
        self.ui_layout.addWidget(self.cmd_bar, 0, Qt.AlignCenter)
        self.ui_layout.addStretch()
        
        self.content_layout.addWidget(self.ui_layer)

        # Initialize State
        # Initialize Spine & Brain
        from corund.tools.router import ToolRouter
        from corund.agent import IntelligentAgent
        self.tool_router = ToolRouter.instance()
        self.agent = IntelligentAgent()
        
        # Connect Signals
        self.tool_router.command_completed.connect(self._on_tool_completed)
        # Connect Visibility Signals (NEXT 6)
        # Connect Visibility Signals (NEXT 6)
        self.agent.thought_emitted.connect(self._on_agent_thought)
        
        # Dual-Surface Emission (Timeline + Terminal)
        self.agent.tool_invocation_emitted.connect(self.workspace.terminal.log_tool_call)
        self.agent.tool_invocation_emitted.connect(self.workspace.timeline.log_tool_call)
        
        self.agent.tool_result_emitted.connect(self.workspace.terminal.log_tool_result)
        self.agent.tool_result_emitted.connect(self.workspace.timeline.log_tool_result)
        
        self.agent.task_result_card_emitted.connect(self.workspace.terminal.log_result_card)
        self.agent.task_result_card_emitted.connect(self.workspace.timeline.log_result_card)
        
        self.agent.task_completed.connect(self._on_agent_task_done)

        # Ensure we start in Home Mode
        self.handle_dock_mode("home")

    def _on_agent_thought(self, thought):
        # Pipe all agent thoughts to both Timeline and Terminal for visibility
        self.workspace.terminal.log_thought(thought)
        self.workspace.timeline.log_thought(thought)

    def check_command(self):
        text = self.cmd_bar.text().lower().strip()
        if not text: return
        self.cmd_bar.clear()
        
        # 1. Direct UI Commands
        if "regression" in text or "soul test" in text:
            self.run_teaching_sequence()
        elif text.startswith("theme "):
            # Theme logic
            pass
        
        # 2. Agentic Commands (NEXT 2)
        elif "fix" in text or "edit" in text or "summarize" in text or "analyze" in text:
            if self.state.mode != "workspace":
                self.handle_dock_mode("workspace")
            self.agent.execute_task(text)
        
        # 3. Simple Chat
        elif "hello" in text:
            from corund.voice import VoiceEngine
            VoiceEngine.instance().speak("Hello. How can I assist you in the workspace today?")

    def _on_agent_task_done(self, success, summary):
        # 1. Voice feedback
        from corund.voice import VoiceEngine
        if success:
            self.avatar.perform_gesture("nod")
            VoiceEngine.instance().speak(f"Task complete. {summary}")
        else:
            VoiceEngine.instance().speak(f"Task failed. {summary}")

        # 2. Fallback Ladder (File Backup)
        try:
            os.makedirs("logs", exist_ok=True)
            with open("logs/last_result.txt", "w", encoding="utf-8") as f:
                f.write(f"STATUS: {'SUCCESS' if success else 'FAILED'}\n")
                f.write(f"SUMMARY: {summary}\n")
        except: pass

    def run_teaching_sequence(self):
        from corund.voice import VoiceEngine
        if not self.avatar.isVisible():
            self.handle_dock_mode("avatar")
        
        # Manifest Rule: Gestures > speech
        self.trigger_biological_action("summon")
        
        # Delay speech to allow gesture to lead
        QTimer.singleShot(1000, lambda: VoiceEngine.instance().speak("Let's look at Regression Analysis."))
        QTimer.singleShot(2500, self._start_holo_flow)

    def trigger_biological_action(self, gesture_name: str):
        """NEXT 5: Biologically connected Avatar actions."""
        self.avatar.perform_gesture(gesture_name)
        
        if gesture_name == "summon":
            # Potential UI sound or highlight
            pass
        elif gesture_name == "swipe":
            # Cycle modes
            modes = ["home", "avatar", "workspace", "notifications", "settings"]
            curr = getattr(self, "_curr_mode_idx", 0)
            next_idx = (curr + 1) % len(modes)
            self._curr_mode_idx = next_idx
            self.handle_dock_mode(modes[next_idx])
        elif gesture_name == "dismiss":
            self.holo_panel.setVisible(False)
            self.handle_dock_mode("home")
        
    def _start_holo_flow(self):
        self.holo_panel.move(650, 180) 
        self.holo_panel.setVisible(True)
        self.holo_panel.show_teaching_sequence()
        self.holo_panel.raise_()
        
        QTimer.singleShot(3000, lambda: self._advance_teaching_step(1))

    def _advance_teaching_step(self, step_idx):
        from corund.voice import VoiceEngine
        # Manifest Rule: No typing animations. Space > clutter.
        dialogues = {
            1: "Observation of raw data.",
            2: "Pattern discovery.",
            3: "Residual analysis.",
            4: "The model is complete."
        }
        
        if step_idx in dialogues:
            # Avatar leads with a nod, then speaks
            self.avatar.perform_gesture("nod") 
            VoiceEngine.instance().speak(dialogues[step_idx])
            
        self.holo_panel.next_step()
        self.holo_panel.raise_() 
        
        if step_idx < 4:
            delay = 4000 
            QTimer.singleShot(delay, lambda: self._advance_teaching_step(step_idx + 1))
        else:
            # Final gesture to close
            QTimer.singleShot(3000, lambda: self.trigger_biological_action("dismiss"))

    def handle_dock_mode(self, mode: str):
        if mode == "home":
            self.status_label.setText("HOME")
        elif mode == "avatar":
            self.status_label.setText("AVATAR ACTIVE")
        elif mode == "workspace":
            self.status_label.setText("WORKSPACE")
        elif mode == "settings":
            self.status_label.setText("SETTINGS")
        else:
            self.status_label.setText(mode.upper())

        # CRITICAL: Visibility Management
        self.avatar.setVisible(False)
        self.workspace.setVisible(False)
        self.holo_panel.setVisible(False)
        self.cmd_bar.setVisible(False)
        self.notif_tray.setVisible(False)
        self.settings_widget.setVisible(False)

        # Reset visuals if not in avatar mode
        if mode != "avatar":
            # Any non-persistent visual cleanup here
            pass

    def handle_dock_mode(self, mode: str):
        if mode == "home":
            self.status_label.setText("HOME")
        elif mode == "avatar":
            self.status_label.setText("AVATAR ACTIVE")
        elif mode == "workspace":
            self.status_label.setText("WORKSPACE")
        elif mode == "settings":
            self.status_label.setText("SETTINGS")
        else:
            self.status_label.setText(mode.upper())

        # CRITICAL: Visibility Management
        self.avatar.setVisible(False)
        self.workspace.setVisible(False)
        self.holo_panel.setVisible(False)
        self.cmd_bar.setVisible(False)
        self.notif_tray.setVisible(False)
        self.settings_widget.setVisible(False)

        if mode == "avatar":
            self.avatar.setVisible(True)
            self.cmd_bar.setVisible(True)
            self.avatar.raise_()
            self.ui_layer.raise_() 
            self.avatar.acknowledge() 
            self.state.set_mode("focus", reason="avatar_summon") 
        elif mode == "home":
            self.state.set_mode("idle", reason="home_dock")
        elif mode == "workspace":
            self.workspace.setVisible(True)
            self.workspace.raise_()
            self.state.set_mode("focus", reason="workspace_dock")
        elif mode == "notifications":
            self.notif_tray.setVisible(True)
            self.notif_tray.raise_()
            self.ui_layer.raise_()
            self.state.set_mode("idle", reason="notif_check")
        elif mode == "settings":
            self.settings_widget.setVisible(True)
            self.settings_widget.raise_()
            self.ui_layer.raise_() 
            self.state.set_mode("idle", reason="settings_view")

    def _on_tool_completed(self, result):
        if result.get("success"):
            self.avatar.perform_gesture("nod")
            from corund.voice import VoiceEngine
            # Verbosity filter will handle this if session is long
            VoiceEngine.instance().speak("Executed successfully.")
        else:
            self.avatar.perform_gesture("nod")
            err = result.get("stderr", result.get("error", ""))
            if err:
                 print(f"[Main] Tool Error: {err}")
