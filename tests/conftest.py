import os
import sys
import importlib.util
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_SHOWCASE_SRC = REPO_ROOT / "web_showcase" / "src"

for path in (REPO_ROOT, WEB_SHOWCASE_SRC):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

def _has(mod: str) -> bool:
    return importlib.util.find_spec(mod) is not None

PYSIDE6_OK = _has("PySide6")
NUMPY_OK = _has("numpy")
DOTENV_OK = _has("dotenv")
PYNPUT_OK = _has("pynput")

# Files that hard-require optional deps (skip at COLLECTION time)
NEEDS_PYSIDE6 = {
    "test_ei_hierarchy.py",
    "test_ei_logic.py",
    "test_mapping_constraints.py",
}
NEEDS_NUMPY = {
    "test_memory.py",
    "test_sensors.py",
}
NEEDS_PYNPUT = {
    "test_sensors.py",
}
NEEDS_DOTENV = {
    "test_tutorial.py",
}

def pytest_ignore_collect(collection_path, config):
    """
    This prevents import-time crashes by skipping entire test modules
    BEFORE pytest imports them.
    """
    name = collection_path.name

    # CI mode: skip UI/voice/device-ish tests aggressively
    etherea_ci = os.getenv("ETHEREA_CI", "").strip() == "1"
    if etherea_ci and any(k in name for k in ("ui", "voice", "audio", "translucency")):
        return True

    if (not PYSIDE6_OK) and (name in NEEDS_PYSIDE6):
        return True
    if (not NUMPY_OK) and (name in NEEDS_NUMPY):
        return True
    if (not PYNPUT_OK) and (name in NEEDS_PYNPUT):
        return True
    if (not DOTENV_OK) and (name in NEEDS_DOTENV):
        return True

    return False

def pytest_collection_modifyitems(config, items):
    """
    Optional extra safety: if something slips through, mark as skipped.
    """
    etherea_ci = os.getenv("ETHEREA_CI", "").strip() == "1"

    skip_ui = pytest.mark.skip(reason="Skipped: PySide6 not installed (UI/Qt tests)")
    skip_numpy = pytest.mark.skip(reason="Skipped: numpy not installed (heavy tests)")
    skip_dotenv = pytest.mark.skip(reason="Skipped: python-dotenv not installed")
    skip_pynput = pytest.mark.skip(reason="Skipped: pynput not installed (device tests)")
    skip_ci = pytest.mark.skip(reason="Skipped in CI (ETHEREA_CI=1): UI/Voice/Device dependent")

    for item in items:
        nid = item.nodeid.lower()

        if (not PYSIDE6_OK) and any(k in nid for k in ("pyside6", "qt", "ui", "translucency")):
            item.add_marker(skip_ui)
        if (not NUMPY_OK) and any(k in nid for k in ("numpy", "sensor", "hid", "memory")):
            item.add_marker(skip_numpy)
        if (not DOTENV_OK) and any(k in nid for k in ("dotenv", "tutorial")):
            item.add_marker(skip_dotenv)
        if (not PYNPUT_OK) and any(k in nid for k in ("pynput", "sensor", "hid", "mouse", "keyboard")):
            item.add_marker(skip_pynput)

        if etherea_ci and any(k in nid for k in ("ui", "voice", "audio", "mic", "hid", "device")):
            item.add_marker(skip_ci)
