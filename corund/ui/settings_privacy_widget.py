from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from corund.ui.juicy_button import JuicyChipButton
from corund.ui.theme import get_theme_manager


class SettingsPrivacyWidget(QFrame):
    avatar_settings_changed = Signal(dict)
    emotion_settings_changed = Signal(dict)
    voice_settings_changed = Signal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("panel", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Settings + Privacy Center")
        title.setObjectName("TitleText")
        subtitle = QLabel("Local-first · Clear toggles")
        subtitle.setStyleSheet("color:#8a90b8;")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(subtitle)
        layout.addLayout(header)

        tabs = QTabWidget()
        tabs.addTab(self._build_appearance_tab(), "Appearance")
        tabs.addTab(self._build_accessibility_tab(), "Accessibility")
        tabs.addTab(self._build_avatar_tab(), "Avatar")
        tabs.addTab(self._build_emotion_tab(), "Emotion")
        tabs.addTab(self._build_voice_tab(), "Voice")
        tabs.addTab(self._build_privacy_tab(), "Privacy")
        layout.addWidget(tabs)

    def _build_appearance_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        title = QLabel("Theme")
        title.setObjectName("TitleText")
        layout.addWidget(title)

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Default Etherea", "Candy"])
        self.theme_selector.currentIndexChanged.connect(self._update_theme)
        layout.addWidget(self.theme_selector)

        layout.addStretch(1)
        return widget

    def _build_accessibility_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        self.reduced_motion = JuicyChipButton("Reduced Motion")
        self.high_contrast = JuicyChipButton("High Contrast")
        self.quiet_mode = JuicyChipButton("Quiet Mode")
        self.dyslexia_spacing = JuicyChipButton("Dyslexia Spacing")
        self.minimal_mode = JuicyChipButton("Minimal Mode")

        for chip in (
            self.reduced_motion,
            self.high_contrast,
            self.quiet_mode,
            self.dyslexia_spacing,
            self.minimal_mode,
        ):
            chip.clicked.connect(self._update_accessibility)
            layout.addWidget(chip)

        layout.addStretch(1)
        return widget

    def _build_avatar_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        self.avatar_enabled = JuicyChipButton("Avatar Enabled")
        self.avatar_free_roam = JuicyChipButton("Free Roam")
        self.avatar_reduce_motion = JuicyChipButton("Reduce Motion")
        self.avatar_freeze = JuicyChipButton("Freeze Avatar")

        for chip in (
            self.avatar_enabled,
            self.avatar_free_roam,
            self.avatar_reduce_motion,
            self.avatar_freeze,
        ):
            chip.clicked.connect(self._update_avatar_settings)
            layout.addWidget(chip)

        layout.addStretch(1)
        return widget

    def _build_emotion_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        self.emotion_enabled = JuicyChipButton("Enable Emotion Engine")
        self.emotion_camera = JuicyChipButton("Enable Camera Sensing (Opt-In)")
        self.emotion_local_only = JuicyChipButton("Local-Only Processing")
        self.emotion_local_only.setChecked(True)
        self.emotion_local_only.setEnabled(False)

        for chip in (self.emotion_enabled, self.emotion_camera):
            chip.clicked.connect(self._update_emotion_settings)
            layout.addWidget(chip)

        layout.addWidget(self.emotion_local_only)

        self.emotion_delete = QPushButton("Delete Emotion Data")
        self.emotion_delete.clicked.connect(self._delete_emotion_data)
        layout.addWidget(self.emotion_delete)

        self.emotion_kill = QPushButton("Kill Switch: Disable Emotion Sensing")
        self.emotion_kill.clicked.connect(self._kill_emotion_engine)
        layout.addWidget(self.emotion_kill)

        layout.addStretch(1)
        return widget

    def _build_privacy_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.addWidget(JuicyChipButton("Microphone Access"))
        layout.addWidget(JuicyChipButton("Camera Access"))
        layout.addWidget(JuicyChipButton("Local Logs Only"))
        layout.addWidget(JuicyChipButton("Offline Mode"))
        layout.addWidget(QLabel("Local-only processing is always on unless you opt-in."))
        layout.addStretch(1)
        return widget

    def _build_voice_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        self.voice_enabled = JuicyChipButton("Enable Voice")
        self.voice_dramatic = JuicyChipButton("Dramatic Mode")

        for chip in (self.voice_enabled, self.voice_dramatic):
            chip.clicked.connect(self._update_voice_settings)
            layout.addWidget(chip)

        layout.addStretch(1)
        return widget

    def _update_theme(self) -> None:
        theme = get_theme_manager()
        selection = self.theme_selector.currentText()
        theme.set_theme("candy" if "Candy" in selection else "default")

    def _update_accessibility(self) -> None:
        theme = get_theme_manager()
        theme.set_accessibility(
            reduced_motion=self.reduced_motion.isChecked(),
            high_contrast=self.high_contrast.isChecked(),
            quiet_mode=self.quiet_mode.isChecked(),
            dyslexia_spacing=self.dyslexia_spacing.isChecked(),
            minimal_mode=self.minimal_mode.isChecked(),
        )

    def _update_avatar_settings(self) -> None:
        self.avatar_settings_changed.emit(
            {
                "enabled": self.avatar_enabled.isChecked(),
                "free_roam": self.avatar_free_roam.isChecked(),
                "reduce_motion": self.avatar_reduce_motion.isChecked(),
                "freeze": self.avatar_freeze.isChecked(),
            }
        )

    def _update_emotion_settings(self) -> None:
        self.emotion_settings_changed.emit(
            {
                "enabled": self.emotion_enabled.isChecked(),
                "camera_opt_in": self.emotion_camera.isChecked(),
            }
        )

    def _delete_emotion_data(self) -> None:
        self.emotion_settings_changed.emit({"delete_data": True})

    def _kill_emotion_engine(self) -> None:
        self.emotion_settings_changed.emit({"kill_switch": True})

    def _update_voice_settings(self) -> None:
        self.voice_settings_changed.emit(
            {
                "enabled": self.voice_enabled.isChecked(),
                "dramatic_mode": self.voice_dramatic.isChecked(),
            }
        )
