from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import json


@dataclass(frozen=True)
class AppSpec:
    app_id: str
    name: str
    path: str
    args: List[str]


class AppRegistry:
    def __init__(self, path: str = "data/apps.json") -> None:
        self._path = Path(path)
        self._apps: Dict[str, AppSpec] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            self._apps = {}
            return
        payload = json.loads(self._path.read_text(encoding="utf-8"))
        apps = payload.get("apps", [])
        self._apps = {
            item["app_id"]: AppSpec(
                app_id=item["app_id"],
                name=item.get("name", item["app_id"]),
                path=item.get("path", ""),
                args=list(item.get("args", [])),
            )
            for item in apps
        }

    def list_apps(self) -> List[AppSpec]:
        return list(self._apps.values())

    def get(self, app_id: str) -> Optional[AppSpec]:
        return self._apps.get(app_id)
