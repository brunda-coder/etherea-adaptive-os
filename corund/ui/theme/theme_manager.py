from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from PySide6.QtCore import QObject, Signal


@dataclass(frozen=True)
class ThemeTokens:
    colors: Dict[str, str]
    radii: Dict[str, int]
    spacing: Dict[str, int]
    font_sizes: Dict[str, int]


VIVID_SOUL_TOKENS = ThemeTokens(
    colors={
        "bg.base": "#0b0d14",
        "bg.panel": "#121524",
        "bg.overlay": "#171a2c",
        "text.primary": "#f3f4ff",
        "text.secondary": "#c2c6ea",
        "text.muted": "#8a90b8",
        "accent.primary": "#6b7cff",
        "accent.secondary": "#8b5bff",
        "state.success": "#3ddc97",
        "state.warning": "#f7b955",
        "state.danger": "#ff6b6b",
        "state.focus": "#7bd5ff",
        "state.calm": "#7ee8c7",
        "ring.calm": "#7ee8c7",
        "ring.focus": "#7bd5ff",
        "ring.stress": "#ff9bb5",
        "ring.idle": "#8d93c5",
    },
    radii={
        "panel": 16,
        "card": 14,
        "chip": 999,
        "button": 12,
    },
    spacing={
        "xs": 8,
        "sm": 16,
        "md": 24,
        "lg": 32,
    },
    font_sizes={
        "title": 18,
        "body": 14,
        "micro": 11,
    },
)

CANDY_TOKENS = ThemeTokens(
    colors={
        "bg.base": "#2a0b3a",
        "bg.panel": "#3a114f",
        "bg.overlay": "#4a1463",
        "text.primary": "#fff4ff",
        "text.secondary": "#f7d3ff",
        "text.muted": "#d3b2ea",
        "accent.primary": "#ff7adf",
        "accent.secondary": "#7ee8ff",
        "state.success": "#6cf2c3",
        "state.warning": "#ffd36c",
        "state.danger": "#ff7aa5",
        "state.focus": "#8ff0ff",
        "state.calm": "#a4f4c2",
        "ring.calm": "#a4f4c2",
        "ring.focus": "#8ff0ff",
        "ring.stress": "#ff9bc7",
        "ring.idle": "#e7b2ff",
    },
    radii={
        "panel": 22,
        "card": 18,
        "chip": 999,
        "button": 16,
    },
    spacing={
        "xs": 10,
        "sm": 18,
        "md": 26,
        "lg": 36,
    },
    font_sizes={
        "title": 20,
        "body": 15,
        "micro": 12,
    },
)


class ThemeManager(QObject):
    theme_changed = Signal()

    def __init__(self, tokens: ThemeTokens | None = None) -> None:
        super().__init__()
        self.theme_name = "default"
        self.tokens = tokens or VIVID_SOUL_TOKENS
        self.reduced_motion = False
        self.high_contrast = False
        self.quiet_mode = False
        self.dyslexia_spacing = False
        self.minimal_mode = False

    def set_accessibility(
        self,
        *,
        reduced_motion: bool | None = None,
        high_contrast: bool | None = None,
        quiet_mode: bool | None = None,
        dyslexia_spacing: bool | None = None,
        minimal_mode: bool | None = None,
    ) -> None:
        if reduced_motion is not None:
            self.reduced_motion = reduced_motion
        if high_contrast is not None:
            self.high_contrast = high_contrast
        if quiet_mode is not None:
            self.quiet_mode = quiet_mode
        if dyslexia_spacing is not None:
            self.dyslexia_spacing = dyslexia_spacing
        if minimal_mode is not None:
            self.minimal_mode = minimal_mode
        self.theme_changed.emit()

    def set_theme(self, name: str) -> None:
        normalized = (name or "").strip().lower()
        if normalized in {"default", "vivid"}:
            self.theme_name = "default"
            self.tokens = VIVID_SOUL_TOKENS
        elif normalized in {"candy", "candy crush", "candy_crush"}:
            self.theme_name = "candy"
            self.tokens = CANDY_TOKENS
        else:
            return
        self.theme_changed.emit()

    def apply_to(self, app) -> None:
        tokens = self.tokens.colors
        radius = self.tokens.radii
        font_sizes = self.tokens.font_sizes
        line_height = "1.55" if self.dyslexia_spacing else "1.25"
        focus_ring = tokens["state.focus"] if not self.high_contrast else "#ffffff"
        panel_border = "#2c3155" if not self.high_contrast else "#ffe3ff"
        panel_bg = tokens["bg.panel"]
        text_primary = tokens["text.primary"]
        text_secondary = tokens["text.secondary"]
        base_bg = tokens["bg.base"]

        qss = f"""
        QWidget {{
            background-color: {base_bg};
            color: {text_primary};
            font-size: {font_sizes['body']}px;
            line-height: {line_height};
            font-family: 'Segoe UI', 'Inter', 'Nunito', sans-serif;
        }}
        QLabel#TitleText {{
            font-size: {font_sizes['title']}px;
            font-weight: 700;
        }}
        QLabel#CandySubtitle {{
            color: {text_secondary};
        }}
        QFrame[panel="true"] {{
            background-color: {panel_bg};
            border: 1px solid {panel_border};
            border-radius: {radius['panel']}px;
        }}
        QLineEdit, QTextEdit {{
            background-color: {tokens['bg.overlay']};
            border: 1px solid {panel_border};
            border-radius: {radius['card']}px;
            padding: 8px 10px;
            color: {text_primary};
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border: 1px solid {focus_ring};
        }}
        QListWidget, QComboBox, QTabWidget::pane {{
            background-color: {tokens['bg.overlay']};
            border: 1px solid {panel_border};
            border-radius: {radius['card']}px;
        }}
        QListWidget::item {{
            padding: 6px 8px;
            border-radius: {radius['card']}px;
        }}
        QListWidget::item:selected {{
            background-color: rgba(107, 124, 255, 0.25);
        }}
        QTabBar::tab {{
            background-color: transparent;
            color: {text_secondary};
            padding: 6px 12px;
        }}
        QTabBar::tab:selected {{
            color: {text_primary};
            border-bottom: 2px solid {tokens['accent.primary']};
        }}
        QToolTip {{
            background-color: {tokens['bg.overlay']};
            color: {text_primary};
            border: 1px solid {panel_border};
            padding: 6px;
        }}
        """

        if self.theme_name == "candy":
            qss += "\n" + _load_candy_qss(tokens, radius)

        app.setStyleSheet(qss)


def _load_candy_qss(tokens: Dict[str, str], radius: Dict[str, int]) -> str:
    qss_path = Path(__file__).with_name("candy_theme.qss")
    if not qss_path.exists():
        return ""
    raw = qss_path.read_text(encoding="utf-8")
    return raw.format(
        base=tokens["bg.base"],
        panel=tokens["bg.panel"],
        overlay=tokens["bg.overlay"],
        text=tokens["text.primary"],
        text_secondary=tokens["text.secondary"],
        accent=tokens["accent.primary"],
        accent2=tokens["accent.secondary"],
        success=tokens["state.success"],
        warning=tokens["state.warning"],
        danger=tokens["state.danger"],
        ring=tokens["ring.calm"],
        card_radius=radius["card"],
        panel_radius=radius["panel"],
        button_radius=radius["button"],
    )


_theme_manager: ThemeManager | None = None


def get_theme_manager() -> ThemeManager:
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
