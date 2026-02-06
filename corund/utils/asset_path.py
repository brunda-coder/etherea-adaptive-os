"""Etherea asset path helper.

Works in:
- Dev mode (normal python run)
- PyInstaller onefile (.exe / AppImage build)

Usage:
    from corund.utils.asset_path import asset
    icon = asset("core/assets/ui/icon.png")
"""

from __future__ import annotations

from corund.resource_manager import ResourceManager


def asset(rel_path: str) -> str:
    """Return absolute path to a bundled asset (best-effort)."""
    return ResourceManager.resolve_path(rel_path)


def asset_optional(rel_path: str, *, corund_specific: bool = False) -> str | None:
    """Return absolute path when an asset exists, else None."""
    return ResourceManager.resolve_asset(rel_path, corund_specific=corund_specific)


def exists(rel_path: str) -> bool:
    """Check if a bundled asset exists."""
    return asset_optional(rel_path, corund_specific=rel_path.startswith("corund/assets/")) is not None
