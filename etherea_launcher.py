
# --- ETHEREA BOOT LOGGER ---
import os, sys, traceback
from datetime import datetime

def _bootlog(msg: str):
    try:
        with open("etherea_boot.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat(timespec='seconds')} | {msg}\n")
    except Exception:
        pass

_bootlog("Launcher started")
_bootlog(f"argv={sys.argv}")
_bootlog(f"cwd={os.getcwd()}")
# --- END BOOT LOGGER ---

import argparse
import os
import sys

try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*a, **k):
        return None  # optional on Termux/CI

# ---------------------------------------------------------------------
# Etherea Launcher (HiDPI-safe) ✅
# Fixes tiny UI on HiDPI displays (Windows + Linux AppImage builds)
# ---------------------------------------------------------------------
# IMPORTANT: Set these BEFORE importing PySide6 / Qt.
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

# ✅ Permanent default scaling for Linux (AppImage often looks tiny otherwise)
if sys.platform.startswith("linux"):
    os.environ.setdefault("QT_SCALE_FACTOR", "1.6")

# ✅ Optional manual override
# Example:
#   ETHEREA_UI_SCALE=2.0 ./EthereaOS_Linux_x86_64.AppImage
if os.environ.get("ETHEREA_UI_SCALE"):
    os.environ["QT_SCALE_FACTOR"] = os.environ["ETHEREA_UI_SCALE"]

# ✅ Windows DPI awareness (helps per-monitor scaling)
if sys.platform.startswith("win"):
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
    except Exception:
        pass

from corund.resource_manager import ResourceManager

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

ResourceManager.configure_qt_plugin_path()

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from corund.app_controller import AppController
from corund.runtime_diagnostics import RuntimeDiagnostics
from corund.perf import get_startup_timer
from corund.ui.recovery_screen import RecoveryScreen

REPORT_URL = "https://github.com/etherea-ai/etherea-adaptive-os/issues/new"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Etherea OS Launcher")
    parser.add_argument("--safe-mode", action="store_true", help="Start in safe mode.")
    parser.add_argument("--self-test", action="store_true", help="Run UI self-test and exit.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    return parser.parse_args(argv)

def main() -> int:
    timer = get_startup_timer()
    timer.mark("launch")
    args = _parse_args(sys.argv[1:])
    if args.safe_mode:
        os.environ["ETHEREA_SAFE_MODE"] = "1"
    if args.debug:
        os.environ["ETHEREA_DEBUG"] = "1"
    if args.self_test and "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"

    load_dotenv()
    diagnostics = RuntimeDiagnostics(debug=args.debug)
    sys.excepthook = diagnostics.log_exception

    # Keep scaling crisp & consistent (prevents weird rounding)
    try:
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except Exception:
        pass

    app = QApplication(sys.argv)
    timer.mark("qt")
    controller = AppController(app, safe_mode=args.safe_mode, diagnostics=diagnostics)
    timer.mark("controller")
    controller = AppController(app, safe_mode=args.safe_mode, diagnostics=diagnostics)

    # Optional: make the default window feel more "app-like" (not tiny)
    try:
        controller.window.resize(1280, 820)
        controller.window.setMinimumSize(1100, 720)
    except Exception:
        pass

    controller.window.setWindowTitle("Etherea – The Living Adaptive OS")
    startup_report = diagnostics.run_startup_checks()
    if not startup_report.ok:
        screen = RecoveryScreen(
            diagnostics,
            startup_report,
            report_url=REPORT_URL,
        )
        screen.show()
        return app.exec()

    controller.start()

    def _run_self_check() -> None:
        report = diagnostics.run_ui_self_check(controller)
        if report.ok:
            diagnostics.mark_self_check_ok()
            if args.self_test:
                diagnostics.write_self_test_marker()
                app.exit(0)
            return
        diagnostics.write_self_test_failure(report.errors)
        screen = RecoveryScreen(
            diagnostics,
            report,
            report_url=REPORT_URL,
        )
        screen.show()
        if args.self_test:
            app.exit(1)

    if args.self_test or diagnostics.should_run_self_check():
        QTimer.singleShot(1200, _run_self_check)

    app.aboutToQuit.connect(controller.shutdown)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
