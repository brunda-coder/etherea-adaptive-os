import sys

from PySide6.QtWidgets import QApplication

from corund.app_controller import AppController

def main():
    """
    The main entry point for the Etherea desktop application.
    """
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Initialize the main application controller
    try:
        controller = AppController(app)
        controller.initialize()
    except Exception as e:
        print(f"FATAL: Could not initialize AppController: {e}")
        # In a real app, show a graphical error message here.
        return -1

    # Show the main window
    controller.window.show()

    # Start the Qt event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
