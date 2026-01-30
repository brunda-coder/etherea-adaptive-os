"""Etherea asset path helper.

Works in:
- Dev mode (normal python run)
- PyInstaller onefile (.exe / AppImage build)

Usage:
    from corund.utils.asset_path import asset
    icon = asset("core/assets/ui/icon.png")
"""

from __future__ import annotations

from pathlib import Path

from corund.app_runtime import resource_path


def asset(rel_path: str) -> str:
    """Return absolute path to a bundled asset."""
    return resource_path(rel_path)


def exists(rel_path: str) -> bool:
    """Check if a bundled asset exists."""
    return Path(resource_path(rel_path)).exists()
