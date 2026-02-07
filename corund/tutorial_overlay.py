from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TutorialStep:
    title: str
    instruction: str
    target: str


class TutorialOverlayStateMachine:
    def __init__(self) -> None:
        self.steps = [
            TutorialStep("Aurora Ring", "This ring reflects your current focus and stress state.", "aurora_ring"),
            TutorialStep("Command Bar", "Speak or type commands in the home command input.", "home_command_input"),
            TutorialStep("Workspace", "Use this button to switch between Drawing, PDF, and Coding modes.", "workspace_selector"),
            TutorialStep("Settings", "Open settings to configure voice, mic, privacy, and connectors.", "settings"),
        ]
        self.index = 0
        self.active = False

    def start(self) -> TutorialStep:
        self.active = True
        self.index = 0
        return self.current()

    def current(self) -> TutorialStep:
        return self.steps[self.index]

    def next(self) -> TutorialStep:
        if self.index < len(self.steps) - 1:
            self.index += 1
        return self.current()

    def done(self) -> bool:
        return self.active and self.index >= len(self.steps) - 1
