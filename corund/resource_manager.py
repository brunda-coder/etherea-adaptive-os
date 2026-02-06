from __future__ import annotations

import os
import sys
from pathlib import Path

from corund.app_runtime import is_frozen, resource_path, resolve_asset_path, user_data_dir


class ResourceManager:
    def __init__(self, base_path: Path | None = None) -> None:
        if base_path is None:
            base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
        self.base_path = base_path

    def resolve(self, relative_path: str) -> str:
        resolved = resolve_asset_path(relative_path, corund_specific=relative_path.startswith("corund/assets/"))
        if resolved:
            return resolved
        return str(self.base_path / relative_path)

    def resolve_optional(self, relative_path: str, *, corund_specific: bool = False) -> str | None:
        return resolve_asset_path(relative_path, corund_specific=corund_specific)

    def exists(self, relative_path: str) -> bool:
        return self.resolve_optional(relative_path, corund_specific=relative_path.startswith("corund/assets/")) is not None

    @staticmethod
    def resolve_path(relative_path: str) -> str:
        return resolve_asset_path(relative_path, corund_specific=relative_path.startswith("corund/assets/")) or resource_path(relative_path)

    @staticmethod
    def resolve_asset(relative_path: str, *, corund_specific: bool = False) -> str | None:
        return resolve_asset_path(relative_path, corund_specific=corund_specific)

    @staticmethod
    def data_dir(app_name: str = "EthereaOS") -> Path:
        return user_data_dir(app_name)

    @staticmethod
    def logs_dir(app_name: str = "EthereaOS") -> Path:
        path = user_data_dir(app_name) / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def configure_qt_plugin_path() -> None:
        if not is_frozen():
            return
        base = Path(getattr(sys, "_MEIPASS", ""))
        plugin_path = base / "PySide6" / "plugins"
        qml_path = base / "PySide6" / "qml"
        if plugin_path.exists():
            os.environ.setdefault("QT_PLUGIN_PATH", str(plugin_path))
            os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", str(plugin_path / "platforms"))
        if qml_path.exists():
            os.environ.setdefault("QML2_IMPORT_PATH", str(qml_path))
