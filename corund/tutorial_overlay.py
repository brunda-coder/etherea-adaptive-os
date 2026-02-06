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
            TutorialStep("Welcome", "Press this command bar and speak or type a command.", "home_command_input"),
            TutorialStep("Workspace", "Press this workspace switch and choose Drawing/PDF/Coding.", "workspace_selector"),
            TutorialStep("Agent", "Press Agent Works to run a dry-run task plan.", "agent_panel"),
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
