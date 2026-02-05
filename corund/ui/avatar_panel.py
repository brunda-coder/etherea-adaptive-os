from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from corund.ui.avatar.avatar_world_widget import AvatarWorldWidget
from corund.ui.juicy_button import JuicyChipButton, JuicyIconButton
from corund.signals import signals



class AvatarPanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("panel", True)
        self.emotion_tag = "calm"
        self.avatar_settings = {
            "enabled": True,
            "free_roam": True,
            "reduce_motion": False,
            "freeze": False,
        }
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Etherea Presence")
        title.setObjectName("TitleText")
        header.addWidget(title)
        header.addStretch(1)
        self.kill_switch = JuicyIconButton("⛔")
        header.addWidget(self.kill_switch)
        layout.addLayout(header)

        self.world = AvatarWorldWidget()
        self.world.setFixedHeight(260)
        layout.addWidget(self.world, alignment=Qt.AlignCenter)

        self.dialogue = QLabel("“Ready when you are. Start a calm focus?”")
        self.dialogue.setWordWrap(True)
        self.dialogue.setStyleSheet("color:#cdd1f6;")
        layout.addWidget(self.dialogue)

        chips = QHBoxLayout()
        focus_chip = JuicyChipButton("Focus ON")
        anchor_chip = JuicyChipButton("Sit near Aurora")
        anchor_chip.clicked.connect(lambda: self.world.go_to_anchor("aurora_ring"))
        chips.addWidget(focus_chip)
        chips.addWidget(anchor_chip)
        layout.addLayout(chips)

        toggles = QHBoxLayout()
        toggles.addWidget(JuicyIconButton("🔊"))
        toggles.addWidget(JuicyIconButton("🎙️"))
        toggles.addStretch(1)
        layout.addLayout(toggles)

        checklist = QLabel("Onboarding: ☐ Connect workspace · ☐ Try a command · ☐ Set focus sprint")
        checklist.setWordWrap(True)
        checklist.setStyleSheet("color:#9aa0c6;")
        layout.addWidget(checklist)

        try:
            signals.tts_requested.connect(self._on_tts_requested)
        except Exception:
            pass

    def update_ei(self, vec: dict) -> None:
        focus = vec.get("focus", 0.5)
        stress = vec.get("stress", 0.2)
        if stress > 0.6:
            self.emotion_tag = "stress"
        elif focus > 0.7:
            self.emotion_tag = "focus"
        else:
            self.emotion_tag = "calm"
        self.world.entity.mood = self.emotion_tag

    def apply_avatar_settings(self, settings: dict) -> None:
        self.avatar_settings.update(settings)
        self.world.set_enabled(self.avatar_settings.get("enabled", True))
        self.world.set_free_roam(self.avatar_settings.get("free_roam", True))
        self.world.set_reduce_motion(self.avatar_settings.get("reduce_motion", False))
        self.world.set_freeze(self.avatar_settings.get("freeze", False))

    def _on_tts_requested(self, text: str, meta: dict) -> None:
        self.world.entity.set_bubble_text(text)
