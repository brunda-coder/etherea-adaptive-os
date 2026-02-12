import logging
import sys
from pathlib import Path

from corund.app_runtime import user_data_dir


def _setup_logging() -> None:
    log_dir = user_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "desktop_startup.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
    )


def _hook_exceptions() -> None:
    logger = logging.getLogger("etherea.main")

    def _excepthook(exc_type, exc, tb):
        logger.exception("Unhandled exception", exc_info=(exc_type, exc, tb))

    sys.excepthook = _excepthook


def main():
    _setup_logging()
    _hook_exceptions()
    logger = logging.getLogger("etherea.main")
    logger.info("Desktop bootstrap start")
    try:
        from PySide6.QtWidgets import QApplication
        from corund.app_controller import AppController
    except Exception as e:
        logger.exception("Desktop dependencies unavailable")
        print(f"FATAL: Desktop dependencies unavailable: {e}")
        return -1

    app = QApplication(sys.argv)

    try:
        controller = AppController(app)
        controller.initialize()
    except Exception as e:
        logger.exception("Could not initialize AppController")
        print(f"FATAL: Could not initialize AppController: {e}")
        return -1

    controller.window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
