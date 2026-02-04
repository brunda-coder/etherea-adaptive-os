from PySide6.QtWidgets import QApplication

from corund.ui.aurora_bar import AuroraBar
from corund.ui.avatar_panel import AvatarPanel
from corund.ui.ethera_dock import EtheraDock
from corund.ui.focus_canvas import FocusCanvas
from corund.ui.settings_privacy_widget import SettingsPrivacyWidget
from corund.ui.status_ribbon import StatusRibbon
from corund.ui.theme import get_theme_manager


def test_ui_widgets_create(qtbot):
    app = QApplication.instance()
    if app:
        get_theme_manager().apply_to(app)

    widgets = [
        AuroraBar(),
        AvatarPanel(),
        EtheraDock(),
        FocusCanvas(),
        SettingsPrivacyWidget(),
        StatusRibbon(),
    ]
    for widget in widgets:
        qtbot.addWidget(widget)
        widget.show()
