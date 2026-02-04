import os
import sys

from corund.resource_manager import ResourceManager

def get_resource_path(relative_path: str) -> str:
    """
    Returns the absolute path to a resource, compatible with both
    development and PyInstaller builds.

    PyInstaller extracts bundled resources into a temporary folder
    accessible via sys._MEIPASS.

    :param relative_path: Path relative to project root or packaged resources
    :return: Absolute path to the resource
    """
    try:
        if hasattr(sys, "_MEIPASS"):
            # PyInstaller runtime
            base_path = sys._MEIPASS
        else:
            # Development runtime
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(base_path, relative_path)
    except Exception as e:
        # Fail gracefully with debug info
        print(
            f"[resource_handler] Error resolving path '{relative_path}': {e}")
        return relative_path  # fallback


# --- Helper functions for common resource types ---

def get_ui_resource(name: str) -> str:
    """Get absolute path to a UI resource file."""
    return ResourceManager.resolve_path(os.path.join("core", "ui", name))


def get_shader_resource(name: str) -> str:
    """Get absolute path to a UI shader resource."""
    return ResourceManager.resolve_path(os.path.join("core", "ui", "shaders", name))


def get_audio_resource(name: str) -> str:
    """Get absolute path to an audio asset."""
    return ResourceManager.resolve_path(os.path.join("assets", "audio", name))
