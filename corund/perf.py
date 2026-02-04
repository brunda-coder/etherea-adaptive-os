from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PhaseTimer:
    enabled: bool = False
    start_time: float = field(default_factory=time.monotonic)
    marks: list[tuple[str, float]] = field(default_factory=list)

    def mark(self, name: str) -> None:
        if not self.enabled:
            return
        self.marks.append((name, time.monotonic()))

    def report(self) -> str:
        if not self.enabled:
            return ""
        parts: list[str] = []
        last = self.start_time
        for name, ts in self.marks:
            delta_ms = int((ts - last) * 1000)
            parts.append(f"{name}={delta_ms}ms")
            last = ts
        total_ms = int((last - self.start_time) * 1000)
        parts.append(f"total={total_ms}ms")
        return " ".join(parts)


_startup_timer = PhaseTimer(enabled=os.environ.get("ETHEREA_PROFILE_STARTUP") == "1")


def get_startup_timer() -> PhaseTimer:
    return _startup_timer


def log_startup_report(report: str) -> None:
    if not report:
        return
    logger = logging.getLogger("etherea.runtime")
    logger.info("Startup profile: %s", report)
    bootlog = Path("etherea_boot.log")
    if bootlog.exists():
        try:
            with bootlog.open("a", encoding="utf-8") as handle:
                handle.write(f"Startup profile: {report}\n")
        except Exception:
            pass
