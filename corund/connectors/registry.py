from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Connector:
    key: str
    label: str
    configured: bool = False
    config_hint: str = "Set token in local settings/environment."


class ConnectorRegistry:
    def __init__(self) -> None:
        self._items = {
            "google_drive": Connector("google_drive", "Google Drive"),
            "github": Connector("github", "GitHub"),
            "calendar": Connector("calendar", "Calendar"),
            "spotify": Connector("spotify", "Spotify"),
            "google_photos": Connector("google_photos", "Google Photos"),
        }

    def list(self) -> list[Connector]:
        return list(self._items.values())

    def set_configured(self, key: str, configured: bool) -> None:
        if key in self._items:
            self._items[key].configured = configured
