import sys


def main():
    """The main entry point for the Etherea desktop application."""
    try:
        from PySide6.QtWidgets import QApplication
        from corund.app_controller import AppController
    except Exception as e:
        print(f"FATAL: Desktop dependencies unavailable: {e}")
        return -1

    app = QApplication(sys.argv)

    try:
        controller = AppController(app)
        controller.initialize()
    except Exception as e:
        print(f"FATAL: Could not initialize AppController: {e}")
        return -1

    controller.window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
