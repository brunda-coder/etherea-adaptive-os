from __future__ import annotations

from core.agent.truth_policy import TruthPolicy


class ToolRouterStub:
    def __init__(self) -> None:
        self.truth_policy = TruthPolicy()

    def handle_user_request(self, text: str) -> str:
        policy = self.truth_policy.enforce(text)
        if policy.flagged:
            return policy.response
        return (
            "I can help with local actions like opening a workspace, running a command, "
            "or summarizing notes. Tell me which you want."
        )
