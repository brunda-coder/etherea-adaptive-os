from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class TruthPolicyResult:
    response: str
    flagged: bool


class TruthPolicy:
    def __init__(self) -> None:
        self._patterns = [
            re.compile(r"\bread my mind\b", re.IGNORECASE),
            re.compile(r"\bguarantee\b", re.IGNORECASE),
            re.compile(r"\b100% certain\b", re.IGNORECASE),
            re.compile(r"\bunlimited knowledge\b", re.IGNORECASE),
        ]

    def enforce(self, text: str) -> TruthPolicyResult:
        if any(p.search(text) for p in self._patterns):
            return TruthPolicyResult(
                response=(
                    "I can’t promise impossible things like mind-reading or absolute certainty. "
                    "I can help by using your local data, tools, and clear options instead."
                ),
                flagged=True,
            )
        return TruthPolicyResult(response=text, flagged=False)
