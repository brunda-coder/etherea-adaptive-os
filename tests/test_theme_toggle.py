import pytest


pytest.importorskip("PySide6")

from corund.ui.theme import get_theme_manager


def test_theme_toggle_updates_tokens():
    theme = get_theme_manager()
    theme.set_theme("default")
    default_color = theme.tokens.colors["bg.base"]

    theme.set_theme("candy")
    candy_color = theme.tokens.colors["bg.base"]

    assert theme.theme_name == "candy"
    assert default_color != candy_color
