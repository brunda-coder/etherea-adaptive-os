import os
import sys
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*a, **k):
        return None  # optional on Termux/CI

from PySide6.QtWidgets import QApplication

from corund.app_controller import AppController


def main() -> int:
    load_dotenv()
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    controller = AppController(app)
    controller.window.show()
    controller.start()

    app.aboutToQuit.connect(controller.shutdown)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
