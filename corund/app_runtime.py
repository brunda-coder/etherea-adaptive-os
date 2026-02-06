from __future__ import annotations

import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False)) or hasattr(sys, "_MEIPASS")


def resource_path(relative: str) -> str:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return str(base / relative)


def resolve_asset_path(relative: str, *, corund_specific: bool = False) -> str | None:
    """Resolve assets across dev/build layouts without hard-crashing callers."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    rel = (relative or "").replace("\\", "/")
    candidates: list[str] = [rel]

    if rel.startswith("core/assets/"):
        candidates.append("assets/" + rel[len("core/assets/"):])
    elif rel.startswith("assets/"):
        candidates.append("core/assets/" + rel[len("assets/"):])

    if corund_specific and not rel.startswith("corund/assets/"):
        if rel.startswith("assets/"):
            candidates.append("corund/assets/" + rel[len("assets/"):])
        elif rel.startswith("core/assets/"):
            candidates.append("corund/assets/" + rel[len("core/assets/"):])

    for candidate in candidates:
        p = (base / candidate).resolve()
        if p.exists():
            return str(p)
    return None


def user_data_dir(app_name: str = "EthereaOS") -> Path:
    override = os.environ.get("ETHEREA_DATA_DIR")
    if override:
        path = Path(override)
        path.mkdir(parents=True, exist_ok=True)
        return path
    if sys.platform.startswith("win"):
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform.startswith("darwin"):
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    path = root / app_name
    path.mkdir(parents=True, exist_ok=True)
    return path
