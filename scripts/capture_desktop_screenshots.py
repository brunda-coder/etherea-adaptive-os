#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    artifacts = Path("artifacts/screenshots_desktop")
    artifacts.mkdir(parents=True, exist_ok=True)

    try:
        import ctypes.util

        if ctypes.util.find_library("GL") is None:
            print("SKIPPED: missing system lib (libGL)")
            print("Manual fallback steps (capture 4 screens):")
            print("  1) Home screen with Aurora ring + avatar bubble")
            print("  2) Tutorial overlay with coach marks")
            print("  3) Workspace hub in Drawing/PDF/Coding mode")
            print("  4) Settings panel with Connectors + Avatar Diagnostics")
            return 0
    except Exception:
        pass

    try:
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication

        from corund.app_controller import AppController
    except Exception as exc:
        print(f"SKIPPED: desktop screenshot dependencies unavailable: {exc}")
        return 0

    app = QApplication([])
    controller = AppController(app)
    controller.initialize()
    window = controller.window

    def capture() -> None:
        window.repaint()
        app.processEvents()
        window.grab().save(str(artifacts / "01_home.png"))

        window._focus_command()
        app.processEvents()
        window.grab().save(str(artifacts / "02_command_palette.png"))

        window.center_stack.setCurrentWidget(window.workspace_hub)
        app.processEvents()
        window.grab().save(str(artifacts / "03_workspace_hub.png"))

        window.center_stack.setCurrentWidget(window.settings_panel)
        app.processEvents()
        window.grab().save(str(artifacts / "04_settings_panel.png"))

        print(f"Saved screenshots to {artifacts}")
        app.quit()

    QTimer.singleShot(1200, capture)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
