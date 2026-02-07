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
            "movement_mode": "wander",
        }
        self._stress_focus = 0.0
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
        anchor_chip = JuicyChipButton("Sit near Aurora")
        anchor_chip.clicked.connect(lambda: self.world.go_to_anchor("aurora_ring"))
        follow_chip = JuicyChipButton("Follow Cursor")
        follow_chip.clicked.connect(lambda: self.world.set_movement_mode("follow"))
        wander_chip = JuicyChipButton("Wander")
        wander_chip.clicked.connect(lambda: self.world.set_movement_mode("wander"))
        chips.addWidget(anchor_chip)
        chips.addWidget(follow_chip)
        chips.addWidget(wander_chip)
        layout.addLayout(chips)

        diag_title = QLabel("Avatar Diagnostics")
        diag_title.setObjectName("TitleText")
        layout.addWidget(diag_title)
        self.diag_assets = QLabel()
        self.diag_expression = QLabel()
        self.diag_movement = QLabel()
        self.diag_stress_focus = QLabel()
        for label in (self.diag_assets, self.diag_expression, self.diag_movement, self.diag_stress_focus):
            label.setStyleSheet("color:#9aa0c6;")
            layout.addWidget(label)
        self._refresh_diagnostics()

        try:
            signals.tts_requested.connect(self._on_tts_requested)
        except Exception:
            pass

    def _refresh_diagnostics(self) -> None:
        diag = self.world.diagnostics()
        self.diag_assets.setText(f"Loaded assets: {diag['assets_count']}")
        self.diag_expression.setText(f"Active expression: {self.emotion_tag}")
        self.diag_movement.setText(f"Movement mode: {diag['movement_mode']}")
        self.diag_stress_focus.setText(f"Stress/Focus score: {self._stress_focus:.2f}")

    def update_ei(self, vec: dict) -> None:
        focus = vec.get("focus", 0.5)
        stress = vec.get("stress", 0.2)
        self._stress_focus = (float(focus) - float(stress) + 1.0) / 2.0
        if stress > 0.6:
            self.emotion_tag = "stress"
        elif focus > 0.7:
            self.emotion_tag = "focus"
        else:
            self.emotion_tag = "calm"
        self.world.entity.mood = self.emotion_tag
        self._refresh_diagnostics()

    def apply_avatar_settings(self, settings: dict) -> None:
        self.avatar_settings.update(settings)
        self.world.set_enabled(self.avatar_settings.get("enabled", True))
        self.world.set_free_roam(self.avatar_settings.get("free_roam", True))
        self.world.set_reduce_motion(self.avatar_settings.get("reduce_motion", False))
        self.world.set_freeze(self.avatar_settings.get("freeze", False))
        if settings.get("movement_mode"):
            self.world.set_movement_mode(settings["movement_mode"])
        self._refresh_diagnostics()

    def _on_tts_requested(self, text: str, meta: dict) -> None:
        self.world.entity.set_bubble_text(text)
        self.world.set_lip_sync_level(float(meta.get("viseme", 0.45)) if isinstance(meta, dict) else 0.35)
