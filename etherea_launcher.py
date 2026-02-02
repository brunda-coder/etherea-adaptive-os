
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

import sys
import os

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

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from corund.app_controller import AppController

def main() -> int:
    load_dotenv()
    # Keep scaling crisp & consistent (prevents weird rounding)
    try:
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except Exception:
        pass

    app = QApplication(sys.argv)
    controller = AppController(app)

    # Optional: make the default window feel more "app-like" (not tiny)
    try:
        controller.window.resize(1280, 820)
        controller.window.setMinimumSize(1100, 720)
    except Exception:
        pass

    controller.window.setWindowTitle("Etherea – The Living Adaptive OS")
    controller.start()

    app.aboutToQuit.connect(controller.shutdown)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
