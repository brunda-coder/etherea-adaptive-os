from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EmotionPrivacy:
    local_only: bool = True
    camera_opt_in: bool = False
    kill_switch: bool = False


class EmotionPrivacyManager:
    def __init__(self) -> None:
        self.state = EmotionPrivacy()

    def set_camera_opt_in(self, enabled: bool) -> None:
        self.state.camera_opt_in = enabled

    def set_kill_switch(self, enabled: bool) -> None:
        self.state.kill_switch = enabled

    def delete_data(self) -> None:
        # Placeholder for deleting stored emotion data.
        self.state = EmotionPrivacy(local_only=True, camera_opt_in=self.state.camera_opt_in, kill_switch=self.state.kill_switch)
