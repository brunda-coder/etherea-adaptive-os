from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QTabWidget, QVBoxLayout, QWidget

from corund.ui.juicy_button import JuicyChipButton
from corund.ui.theme import get_theme_manager


class SettingsPrivacyWidget(QFrame):
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
        tabs.addTab(self._build_accessibility_tab(), "Accessibility")
        tabs.addTab(self._build_privacy_tab(), "Privacy")
        tabs.addTab(self._build_audio_tab(), "Audio")
        layout.addWidget(tabs)

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

    def _build_privacy_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.addWidget(JuicyChipButton("Microphone Access"))
        layout.addWidget(JuicyChipButton("Camera Access"))
        layout.addWidget(JuicyChipButton("Local Logs Only"))
        layout.addWidget(JuicyChipButton("Offline Mode"))
        layout.addStretch(1)
        return widget

    def _build_audio_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.addWidget(JuicyChipButton("Background Audio"))
        layout.addWidget(JuicyChipButton("Voice Output"))
        layout.addWidget(JuicyChipButton("UI Sound FX"))
        layout.addStretch(1)
        return widget

    def _update_accessibility(self) -> None:
        theme = get_theme_manager()
        theme.set_accessibility(
            reduced_motion=self.reduced_motion.isChecked(),
            high_contrast=self.high_contrast.isChecked(),
            quiet_mode=self.quiet_mode.isChecked(),
            dyslexia_spacing=self.dyslexia_spacing.isChecked(),
            minimal_mode=self.minimal_mode.isChecked(),
        )
